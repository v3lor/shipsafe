# Release decision: GO

GO for this simulated scenario

Local synthetic SQLite simulation; not a production safety guarantee.

Migration: `migrations/candidate.sql`
SQL SHA-256: `dad33ddc613b7f8f99150e547a44f130aea02c07f24526ea6b149f1e66f09448`

Seeded orders: 5
Measured elapsed seconds: 0.045636

## migration: PASS

Measured seconds: 0.004341

```json
{
  "statements_in_script": 1
}
```

## preservation: PASS

Measured seconds: 0.001248

```json
{
  "count_before": 5,
  "count_after": 5,
  "preserved_orders": [
    {
      "id": 1,
      "customer_label": "Demo Cedar",
      "address": "1 Imaginary Lane",
      "status": "pending"
    },
    {
      "id": 2,
      "customer_label": "Demo Orbit",
      "address": null,
      "status": "pending"
    },
    {
      "id": 3,
      "customer_label": "Demo O'Clock",
      "address": "",
      "status": "shipped"
    },
    {
      "id": 4,
      "customer_label": "Demo Café",
      "address": "Unit Ω, Fictional Station",
      "status": "delivered"
    },
    {
      "id": 5,
      "customer_label": "Demo Parcel",
      "address": "Line one\nLine two — invented",
      "status": "pending"
    }
  ]
}
```

## old-version: PASS

Measured seconds: 0.005981

```json
{
  "read_seed_id": 1,
  "created_order": {
    "id": 6,
    "customer_label": "Demo Rollout",
    "address": null,
    "status": "pending"
  }
}
```

## new-version: PASS

Measured seconds: 0.011930

```json
{
  "legacy_order": {
    "id": 1,
    "customer_label": "Demo Cedar",
    "address": "1 Imaginary Lane",
    "status": "pending",
    "delivery_window": null
  },
  "created_order": {
    "id": 7,
    "customer_label": "Demo New App",
    "address": "Imaginary depot",
    "status": "pending",
    "delivery_window": "9–12"
  },
  "optional_order_id": 8
}
```

## rollback: PASS

Measured seconds: 0.006919

```json
{
  "v2_order_read_by_v1": {
    "id": 7,
    "customer_label": "Demo New App",
    "address": "Imaginary depot",
    "status": "pending"
  },
  "created_order": {
    "id": 9,
    "customer_label": "Demo Rollback",
    "address": "Fictional locker",
    "status": "pending"
  },
  "orders_columns": [
    "id",
    "customer_label",
    "address",
    "status",
    "delivery_window"
  ]
}
```

## Investigation and remediation

Gate evidence above is observed. IBM Bob IDE should investigate the failure, implement and verify the repair, then document the root cause and exact remediation. This generated report does not claim that work has occurred.
