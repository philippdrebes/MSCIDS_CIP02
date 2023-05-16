create schema cip;
use cip;

create table komoot
(
    id             int auto_increment,
    title          nvarchar(512)  null,
    difficulty     nvarchar(50)   null,
    distance       decimal(10, 2) null,
    elevation_up   decimal(10, 2) null,
    elevation_down decimal(10, 2) null,
    duration       decimal(10, 2) null,
    speed          decimal(10, 2) null,
    gpx_file       nvarchar(512)  null,
    link           nvarchar(512)  null,
    constraint komoot_pk
        primary key (id)
);

create table schweizmobil
(
    id               int auto_increment,
    url              nvarchar(512)  null,
    name             nvarchar(512)  null,
    distance         decimal(10, 2) null,
    altitude_up      decimal(10, 2) null,
    altitude_down    decimal(10, 2) null,
    duration         decimal(10, 2) null,
    difficulty_level nvarchar(50)   null,
    fitness_level    nvarchar(50)   null,
    constraint schweizmobil_pk
        primary key (id)
);


create table routes
(
    id             int auto_increment,
    title          nvarchar(512),
    source         nvarchar(20),
    distance       decimal(10, 2) null,
    elevation_up   decimal(10, 2) null,
    elevation_down decimal(10, 2) null,
    duration       time           null,
    difficulty     nvarchar(50)   null,
    link           nvarchar(512)  null,

    constraint routes_pk
        primary key (id)
);