import logging

from celery.result import AsyncResult
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from api.v1.serializers.report_serializers import ReportCreateSerializer
from celery_app.tasks.report_tasks import generate_report_task

logger = logging.getLogger(__name__)

"""
APIView для запуска генерации отчёта в фоне через Celery.
Параметры передаются через GET, но мы валидируем их с помощью ReportParamsSerializer.
"""


class ReportView(APIView):
    def get(self, request, *args, **kwargs):
        serializer = ReportCreateSerializer(data=request.query_params)
        serializer.is_valid(raise_exception=True)

        task = generate_report_task.delay(
            serializer.validated_data["start_date"],
            serializer.validated_data["end_date"],
        )
        logger.info(f"Report generation task submitted, task_id={task.id}")

        return Response({"task_id": task.id}, status=status.HTTP_202_ACCEPTED)


class ReportResultView(APIView):
    """
    APIView для проверки статуса задачи генерации отчёта.
    GET-параметр:
      - task_id: ID задачи, полученной при запуске.
    """

    def get(self, request, *args, **kwargs):
        task_id = request.query_params.get("task_id")
        if not task_id:
            return Response(
                {"detail": "task_id is required."}, status=status.HTTP_400_BAD_REQUEST
            )

        result = AsyncResult(task_id)
        if result.ready():
            return Response(
                {"status": result.status, "result": result.result},
                status=status.HTTP_200_OK,
            )
        else:
            return Response({"status": result.status}, status=status.HTTP_202_ACCEPTED)
