# Extension rules

## Когда разрешено создавать новый profile

Новый profile разрешён только если одновременно выполняется хотя бы одно условие:
- другой deploy primitive;
- другой rollback primitive;
- другой тип release artifact;
- другой способ health observation;
- другая promotion topology.

## Когда новый profile запрещён

Если различия ограничиваются:
- именами сервисов;
- портами;
- health endpoints;
- таймингами;
- smoke командами;
- доменами;
- optional staging;
- feature flags;
то нужен override, а не новый profile.

## Требования к новому profile

1. `profiles/<name>.yaml`
2. соответствие `deployment-profile.schema.yaml`
3. пример project override
4. пример environment override
5. smoke/rollback/observe examples
6. минимум 3 scenario tests
7. один shadow run без real promotion

## Migration rule

При смене инфраструктуры проект не должен переписывать skill.
Проект должен:
- выбрать новый profile;
- заполнить override data;
- прогнать scenario suite;
- только потом разрешить promotion.
