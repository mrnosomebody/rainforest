from datetime import datetime
from decimal import Decimal

from django.db.models import DecimalField, ExpressionWrapper, F, QuerySet, Sum

from orders.enums import OrderStatus
from orders.models import Order, OrderItem


def generate_summary_report(start_date: datetime, end_date: datetime) -> dict:
    completed_orders = Order.objects.filter(
        created_at__gte=start_date,
        created_at__lte=end_date,
        status=OrderStatus.COMPLETED,
    )

    return {
        "total_revenue": _get_total_revenue(orders=completed_orders),
        "profit": _get_profit(orders=completed_orders),
        "units_sold": _get_units_sold(orders=completed_orders),
        "number_of_returns": _get_returns_count(start_date, end_date),
    }


def _get_total_revenue(orders: QuerySet[Order]) -> Decimal:
    """Общая выручка: сумма (price_at_purchase * quantity) по всем позициям завершенных заказов"""
    revenue_agg = OrderItem.objects.filter(order__in=orders).aggregate(
        total_revenue=Sum(
            ExpressionWrapper(
                F("price_at_purchase") * F("quantity"), output_field=DecimalField()
            )
        )
    )
    return revenue_agg["total_revenue"] or Decimal("0.00")


def _get_profit(orders: QuerySet[Order]) -> Decimal:
    """Прибыль: для каждой позиции считаем (price_at_purchase - product__cost) * quantity"""
    profit_agg = OrderItem.objects.filter(order__in=orders).aggregate(
        profit=Sum(
            ExpressionWrapper(
                (F("price_at_purchase") - F("product__cost")) * F("quantity"),
                output_field=DecimalField(),
            )
        )
    )
    return profit_agg["profit"] or Decimal("0.00")


def _get_returns_count(start_date: datetime, end_date: datetime) -> int:
    return Order.objects.filter(
        created_at__gte=start_date,
        created_at__lte=end_date,
        status=OrderStatus.CANCELED,
    ).count()


def _get_units_sold(orders: QuerySet[Order]) -> int:
    """Количество проданных единиц: суммируем quantity по всем позициям завершенных заказов"""
    units_sold_agg = OrderItem.objects.filter(order__in=orders).aggregate(
        units_sold=Sum("quantity")
    )
    return units_sold_agg["units_sold"] or 0
