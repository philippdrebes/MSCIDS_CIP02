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

