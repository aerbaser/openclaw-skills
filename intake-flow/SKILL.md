---
name: intake-flow
version: 1.0.0
description: "Project intake flow: clarify → brief → route (research/brainstorm/work). Handles buttons: intake_research_brainstorm, intake_brainstorm, intake_work."
triggers:
  - user brings new project idea or task
  - callback_data starts with "intake_"
  - user says "у меня есть идея", "хочу сделать", "давай запустим", "новый проект", "новая задача"
metadata:
  { "openclaw": { "emoji": "🎯" } }
---

# Intake Flow — Протокол приёма проекта

## Когда активировать

1. Юра описывает новую идею / проект / задачу
2. `callback_data` начинается на `intake_` (кнопки approval)
3. Юра явно говорит "у меня идея", "хочу запустить X", "новый проект"

**НЕ активировать:** если это вопрос/статус/команда без новой идеи.

---

## ЧАСТЬ A: Первичный Intake (новая идея)

### Шаг 1: Уточнения

Задай **3–5 вопросов в ОДНОМ сообщении**:

```
Уточни быстро:

1. Цель — что должен делать результат?
2. Стек / платформа (web, mobile, скрипт, bot, smart contract, ...)?
3. MVP или полная реализация?
4. Есть ли deadline / приоритет?
5. Что уже есть / пробовали?
```

Адаптируй под контекст — не спрашивай очевидное.

### Шаг 2: Brief

После ответов сформируй brief:

```
**Brief: [Название]**
Цель: [1-2 строки]
Контекст: [что есть, что известно]
Стек: [технологии]
Ограничения: [если есть]
Ожидаемый результат: [конкретный артефакт]
```

Сохрани brief в файл:
```bash
cat > ~/clawd/memory/intake-brief-current.md << 'BRIEF'
# Intake Brief — Current
last_updated: [ISO timestamp]
flow: pending

## Brief: [Название]
Цель: ...
Контекст: ...
Стек: ...
Ограничения: ...
Ожидаемый результат: ...
BRIEF
```

### Шаг 3: Кнопки выбора флоу

Отправь brief + кнопки:

```python
message(
  action="send",
  message="[Brief выше]\n\nВыбери флоу:",
  buttons=[[
    {"text": "🔬 Ресерч + 💡 Брейншторм", "callback_data": "intake_research_brainstorm"},
    {"text": "💡 Брейншторм", "callback_data": "intake_brainstorm"},
    {"text": "🚀 В работу", "callback_data": "intake_work"}
  ]]
)
```

---

## ЧАСТЬ B: Обработка кнопок (callback_data)

### B1: `intake_research_brainstorm`

1. Прочитай brief из `~/clawd/memory/intake-brief-current.md`
2. Напиши Юре: "Запускаю ресерч у Аристотеля. Вернусь с результатами через 10–20 мин."
3. Запиши в INBOX Аристотеля (`~/.openclaw/shared-memory/communication/inbox_aristotle.md`):

```markdown
## [DATE] Ресерч для Intake

**Задача:** Deep research по теме:

[Вставь весь brief]

**Формат ответа:**
- Ключевые игроки / аналоги
- Технические подходы (3–5 вариантов)
- Риски и ограничения
- Рекомендация: какой подход лучше и почему

**По завершении:** отправь результаты через sessions_send → Сократ (topic:121)
**Timeout:** 20 мин
```

4. `sessions_send(label="aristotle", message="Inbox обновлён: новый ресерч-запрос")`
5. Обнови working-buffer:

```bash
python3 -c "
import json, datetime
d = json.load(open('/home/aiadmin/clawd/memory/working-buffer.json'))
d['intake_state'] = {
    'active': True, 'flow': 'research_brainstorm',
    'brainstorm_waiting': False, 'intake_cron_id': None,
    'brief_file': '~/clawd/memory/intake-brief-current.md',
    'stage': 'waiting_research'
}
d['last_updated'] = datetime.datetime.now(datetime.UTC).isoformat()
json.dump(d, open('/home/aiadmin/clawd/memory/working-buffer.json','w'), indent=2, ensure_ascii=False)
print('OK')
"
```

6. **Когда Аристотель вернёт результаты** → перейди к **B2** (`intake_brainstorm`) с research context.

---

### B2: `intake_brainstorm`

1. Прочитай brief из `~/clawd/memory/intake-brief-current.md`
2. Если есть research context от Аристотеля — включи его

**Запуск Brainstorm Claude:**

Напиши в Brainstorm Claude (topic:3 или topic:4 через sessions_send):

```
Brainstorm сессия.

[Вставь brief]

[Если есть: === Research Context ===\n[результаты Аристотеля]]

Задавай вопросы по одному. Исследуй идею глубоко: риски, альтернативы, нестандартные решения.
```

`sessions_send(label="brainstorm-claude", message="[текст выше]")`

**Запуск таймера (5 мин):**

```python
cron(
  action="add",
  job={
    "name": "intake-brainstorm-timer",
    "schedule": {"kind": "at", "at": "[NOW + 5 MINUTES ISO]"},
    "payload": {
      "kind": "systemEvent",
      "text": "INTAKE_BRAINSTORM_TIMEOUT: Юра не ответил на вопрос брейншторма. Сократ: прочитай последний вопрос из brainstorm-claude сессии и ответь от лица Юры: 'Продолжай — атакуй с разных углов: риски, альтернативы, что может сломаться, нестандартные решения.'"
    },
    "sessionTarget": "main",
    "delivery": {"mode": "none"}
  }
)
```

Сохрани cronJobId в working-buffer:

```bash
python3 -c "
import json, datetime
d = json.load(open('/home/aiadmin/clawd/memory/working-buffer.json'))
d['intake_state']['brainstorm_waiting'] = True
d['intake_state']['stage'] = 'brainstorm_active'
d['intake_state']['intake_cron_id'] = '[JOB_ID]'  # ID из ответа cron
d['last_updated'] = datetime.datetime.now(datetime.UTC).isoformat()
json.dump(d, open('/home/aiadmin/clawd/memory/working-buffer.json','w'), indent=2, ensure_ascii=False)
"
```

Сообщи Юре: "Брейншторм запущен. Brainstorm Claude задаст вопрос. Если не ответишь за 5 мин — отвечу сам."

**Когда Юра отвечает во время брейншторма:**
- Сбрось флаг: `intake_state.brainstorm_waiting = false`
- Таймер автоматически станет no-op (проверит флаг и завершится)
- Перенаправь ответ в Brainstorm Claude

**Когда INTAKE_BRAINSTORM_TIMEOUT системный ивент приходит:**
- Проверь `working-buffer.json → intake_state.brainstorm_waiting`
- Если `true` → прочитай последний вопрос из brainstorm-claude сессии → ответь: "Продолжай — атакуй с разных углов: риски, альтернативы, что может сломаться, нестандартные решения."
- Если `false` → Юра уже ответил, no-op

**Завершение брейншторма:**
Когда Brainstorm Claude закончил → собери итог → покажи Юре:

```
**Итог брейншторма:**
[summary 5-7 пунктов]

Отправить в Платон для планирования?
[Да → Платон] [Нет, доработать]
```

Кнопки: `callback_data: "intake_work"` и `callback_data: "intake_brainstorm_more"`

---

### B3: `intake_work`

1. Прочитай brief из `~/clawd/memory/intake-brief-current.md`
2. Собери всё: brief + research (если было) + brainstorm summary (если было)

**Запиши задачу в INBOX Платона** (`~/.openclaw/shared-memory/communication/inbox_platon.md`):

```markdown
## [DATE] Новый проект от Юры

**Brief:**
[Вставь brief]

**Research summary:** [если было]

**Brainstorm summary:** [если было]

**Задача:**
1. Создай детальный план реализации
2. Разбей на GitHub Issues (в репо sokrat-core если не указано другое)
3. Issues должны быть AO-ready: чёткий acceptance criteria, стек, тесты
4. Вернись с планом и ссылками на Issues

**Ожидаемый артефакт:** список GitHub Issues + порядок выполнения
**Timeout:** 15 мин
```

3. `sessions_send(label="platon", message="Inbox обновлён: новый проект для планирования")`

4. Обнови working-buffer:

```bash
python3 -c "
import json, datetime
d = json.load(open('/home/aiadmin/clawd/memory/working-buffer.json'))
d['intake_state'] = {
    'active': True, 'flow': 'work', 'stage': 'waiting_platon',
    'brainstorm_waiting': False, 'intake_cron_id': None,
    'brief_file': '~/clawd/memory/intake-brief-current.md'
}
d['last_updated'] = datetime.datetime.now(datetime.UTC).isoformat()
json.dump(d, open('/home/aiadmin/clawd/memory/working-buffer.json','w'), indent=2, ensure_ascii=False)
"
```

5. Сообщи Юре: "Передал Платону. Он создаст план и Issues. AO подхватит автоматически. Вернусь со статусом через 15 мин."

---

## Правила

- Brief ВСЕГДА сохранять в `~/clawd/memory/intake-brief-current.md` (перезапись при новом intake)
- Не запускать флоу без brief
- Таймер 5 мин — только один активный за раз (проверь `intake_cron_id` перед созданием)
- После завершения флоу: `intake_state.active = false`
- Платон → AO автоматически (не нужно ждать Юру)
- Brainstorm результаты всегда показывать Юре перед отправкой в Платон
