PRAGMA foreign_keys=OFF;
BEGIN TRANSACTION;
CREATE TABLE account_values (
        id integer,
        available_balance float,
        model_id bigint,
        timestamp timestamp,
        total_value float,
        primary key (id)
    );
CREATE TABLE conversations (
        id integer,
        model_id bigint,
        prompt varchar(1000),
        response varchar(1000),
        timestamp timestamp,
        primary key (id)
    );
CREATE TABLE models (
        id integer,
        created_at timestamp,
        initial_capital float,
        model_name varchar(255) not null,
        name varchar(255) not null,
        provider_id bigint,
        primary key (id)
    );
INSERT INTO models VALUES(1,NULL,10000.0,'gpt-3.5-turbo','Default Trading Model',1);
CREATE TABLE portfolios (
        id integer,
        avg_price float,
        coin varchar(255) not null,
        leverage integer,
        model_id bigint,
        quantity float not null,
        side varchar(255),
        updated_at timestamp,
        primary key (id)
    );
CREATE TABLE providers (
        id integer,
        api_key varchar(255) not null,
        api_url varchar(255) not null,
        created_at timestamp,
        models varchar(255),
        name varchar(255) not null,
        primary key (id)
    );
INSERT INTO providers VALUES(1,'your-binance-api-key','https://api.binance.com',NULL,NULL,'Binance');
CREATE TABLE settings (
        id integer,
        key varchar(255) not null,
        value varchar(255) not null,
        primary key (id)
    );
CREATE TABLE trades (
        id integer,
        coin varchar(255) not null,
        fee float,
        leverage integer,
        model_id bigint,
        pnl float,
        price float not null,
        quantity float not null,
        side varchar(255),
        signal varchar(255) not null,
        timestamp timestamp,
        primary key (id)
    );
COMMIT;