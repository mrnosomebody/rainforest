# Run

`docker compose up --build -d`

# Tests

1. `export DB_HOST=localhost`
2. `poetry run pytest`
3. `poetry run coverage run -m pytest`
4. `poetry run coverage report`

```
Name                                           Stmts   Miss Branch BrPart  Cover
--------------------------------------------------------------------------------
orders/__init__.py                                 0      0      0      0   100%
orders/apps.py                                     3      0      0      0   100%
orders/constants.py                                0      0      0      0   100%
orders/dto.py                                      9      0      0      0   100%
orders/enums.py                                    5      0      0      0   100%
orders/migrations/0001_initial.py                  7      0      0      0   100%
orders/migrations/__init__.py                      0      0      0      0   100%
orders/models.py                                  14      1      0      0    93%
orders/services/__init__.py                        0      0      0      0   100%
orders/services/order.py                          50     10     12      2    77%
orders/services/order_item.py                     10      0      2      0   100%
orders/tests/__init__.py                           0      0      0      0   100%
orders/tests/test_unit/__init__.py                 0      0      0      0   100%
orders/tests/test_unit/test_order_service.py      18      0      0      0   100%
products/__init__.py                               0      0      0      0   100%
products/apps.py                                   3      0      0      0   100%
products/migrations/0001_initial.py                6      0      0      0   100%
products/migrations/__init__.py                    0      0      0      0   100%
products/models.py                                 8      0      0      0   100%
--------------------------------------------------------------------------------
TOTAL                                            133     11     14      2    90%

```
