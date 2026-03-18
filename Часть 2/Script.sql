Таблицы базы данных

CREATE TABLE IF NOT EXISTS executor (
    id     SERIAL PRIMARY KEY,
    name   VARCHAR(255) NOT NULL,
    inn    VARCHAR(20),
    addres TEXT,
    phone  VARCHAR(30)
);

CREATE TABLE IF NOT EXISTS customers (
    id       VARCHAR(20) PRIMARY KEY,
    name     VARCHAR(255) NOT NULL,
    inn      VARCHAR(20),
    addres   TEXT,
    phone    VARCHAR(30),
    salesman BOOLEAN NOT NULL DEFAULT FALSE,
    buyer    BOOLEAN NOT NULL DEFAULT FALSE
);

CREATE TABLE IF NOT EXISTS materials (
    id   SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    cost NUMERIC(15, 2) NOT NULL DEFAULT 0,
    unit VARCHAR(50)
);

CREATE TABLE IF NOT EXISTS prices (
    id          SERIAL PRIMARY KEY,
    material_id INTEGER NOT NULL REFERENCES materials(id) ON DELETE CASCADE,
    cost        NUMERIC(15, 2) NOT NULL,
    date        DATE NOT NULL DEFAULT CURRENT_DATE
);

CREATE TABLE IF NOT EXISTS product (
    id   SERIAL PRIMARY KEY,
    code VARCHAR(50),
    name VARCHAR(255) NOT NULL,
    unit VARCHAR(50)
);

CREATE TABLE IF NOT EXISTS specification (
    id         SERIAL PRIMARY KEY,
    name       VARCHAR(255) NOT NULL,
    product_id INTEGER NOT NULL REFERENCES product(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS specification_items (
    id          SERIAL PRIMARY KEY,
    spec_id     INTEGER NOT NULL REFERENCES specification(id) ON DELETE CASCADE,
    material_id INTEGER NOT NULL REFERENCES materials(id) ON DELETE RESTRICT,
    quantity    NUMERIC(15, 4) NOT NULL DEFAULT 0
);

CREATE TABLE IF NOT EXISTS buyer_order (
    id           SERIAL PRIMARY KEY,
    order_number VARCHAR(50) NOT NULL,
    date         DATE NOT NULL DEFAULT CURRENT_DATE,
    executor_id  INTEGER NOT NULL REFERENCES executor(id) ON DELETE RESTRICT,
    customer_id  VARCHAR(20) NOT NULL REFERENCES customers(id) ON DELETE RESTRICT
);

CREATE TABLE IF NOT EXISTS order_items (
    id         SERIAL PRIMARY KEY,
    order_id   INTEGER NOT NULL REFERENCES buyer_order(id) ON DELETE CASCADE,
    product_id INTEGER NOT NULL REFERENCES product(id) ON DELETE RESTRICT,
    quantity   NUMERIC(15, 4) NOT NULL DEFAULT 1,
    price      NUMERIC(15, 2) NOT NULL DEFAULT 0
);

CREATE TABLE IF NOT EXISTS production (
    id               SERIAL PRIMARY KEY,
    number           VARCHAR(50) NOT NULL,
    date             DATE NOT NULL DEFAULT CURRENT_DATE,
    specification_id INTEGER NOT NULL REFERENCES specification(id) ON DELETE RESTRICT
);

CREATE TABLE IF NOT EXISTS production_items (
    id            SERIAL PRIMARY KEY,
    production_id INTEGER NOT NULL REFERENCES production(id) ON DELETE CASCADE,
    material_id   INTEGER NOT NULL REFERENCES materials(id) ON DELETE RESTRICT,
    quantity_used NUMERIC(15, 4) NOT NULL DEFAULT 0
);

Импорт данных из json

INSERT INTO customers (id, name, inn, addres, phone, salesman, buyer)
VALUES
    ('000000001', 'ООО "Поставка"',        '',            'г.Пятигорск',                    '+79198634592', TRUE,  TRUE),
    ('000000002', 'ООО "Кинотеатр Квант"', '26320045123', 'г. Железноводск, ул. Мира, 123', '+79884581555', TRUE,  FALSE),
    ('000000008', 'ООО "Новый JDTO"',      '26320045111', 'г. Железноводсу',                '+79884581555', TRUE,  FALSE),
    ('000000003', 'ООО "Ромашка"',         '4140784214',  'г. Омск, ул. Строителей, 294',   '+79882584546', FALSE, TRUE),
    ('000000009', 'ООО "Ипподром"',        '5874045632',  'г. Уфа, ул. Набережная, 37',     '+79627486389', TRUE,  TRUE),
    ('000000010', 'ООО "Ассоль"',          '2629011278',  'г. Калуга, ул. Пушкина, 94',     '+79184572398', FALSE, TRUE)
ON CONFLICT (id) DO NOTHING;

Запрос расчёта полной стоимости заказа покупателя

SELECT
    bo.id AS order_id,
    bo.order_number,
    bo.date AS order_date,
    c.name AS customer_name,
    SUM(
        oi.quantity * oi.price
        + oi.quantity * COALESCE(mat_cost.material_cost_per_unit, 0)
    ) AS total_order_cost
FROM buyer_order bo
JOIN customers c ON c.id = bo.customer_id
JOIN order_items oi ON oi.order_id = bo.id
LEFT JOIN specification s ON s.product_id = oi.product_id
LEFT JOIN LATERAL (
    SELECT SUM(si.quantity * m.cost) AS material_cost_per_unit
    FROM specification_items si
    JOIN materials m ON m.id = si.material_id
    WHERE si.spec_id = s.id
) mat_cost ON TRUE
GROUP BY bo.id, bo.order_number, bo.date, c.name
ORDER BY bo.id;
