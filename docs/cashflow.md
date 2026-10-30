# Cashflow Sheet

Cost:

```
=ARRAYFORMULA(
    IF(
        Oct_2026[Price]="", "",
        IF(Oct_2026[Item Count]="", 1, Oct_2026[Item Count]) * Oct_2026[Price]
    )
)
```

Expenses:

```
=SUMIF(
    Oct_2026[Cost], ">0"
)
```

Expenses Cash:

```
=SUMIFS(
    Oct_2026[Cost],
    Oct_2026[By Card], FALSE,
    Oct_2026[Cost], ">0"
)
```

Expenses Card:

```
=SUMIFS(
    Oct_2026[Cost],
    Oct_2026[By Card], TRUE,
    Oct_2026[Cost], ">0"
)
```

Income:

```
=ABS(
    SUMIF(
        Oct_2026[Cost], "<0"
    )
)
```

Income Cash:

```
=ABS(
    SUMIFS(
        Oct_2026[Cost],
        Oct_2026[By Card], FALSE,
        Oct_2026[Cost], "<0"
    )
)
```

Income Card:

```
=ABS(
    SUMIFS(
        Oct_2026[Cost],
        Oct_2026[By Card], TRUE,
        Oct_2026[Cost], "<0"
    )
)
```

Date Coercion:

```
=ARRAYFORMULA(
    IF(
        ISBLANK(Sep_2026[Date]), "",
        IFERROR(
            VALUE(SUBSTITUTE(Sep_2026[Date], CHAR(160), " ")), Sep_2026[Date]
        )
    )
)
```
