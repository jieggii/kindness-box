/* points */
create table points(
    point_id serial primary key,
    locality varchar not null,
    address  varchar not null
);
comment on column points.point_id is 'ID of the point';
comment on column points.locality is 'Name of the city or town';
comment on column points.address is 'Address of the point';

comment on table points is 'Points where donators bring gifts';

/* donators */
create table donators
(
    donator_id serial primary key,
    vk_user_id integer not null,
    name varchar not null,
    org_name varchar default null,
    phone_number varchar not null,
    brought_gifts bool default false,
    point_id integer not null,
    constraint donators_fk_point_id foreign key (point_id) references points (point_id)
);

comment on column donators.donator_id is 'ID of the donator';
comment on column donators.vk_user_id is 'VK user id of the donator';
comment on column donators.name is 'Name of the donator';
comment on column donators.org_name is 'Name of the donating organization (optional)';
comment on column donators.phone_number is 'Phone number of the donator or donating organization';
comment on column donators.brought_gifts is 'Have the donator already brought to the point?';
comment on column donators.point_id is 'ID of the point donator belongs to';

comment on table donators is 'People who choose persons and bring gifts';

/* persons */
create table persons
(
    person_id serial primary key,
    name varchar not null,
    age integer not null,
    gift text not null,
    donator_id integer,
    constraint persons_fk_donator_id foreign key (donator_id) references donators (donator_id),
    point_id integer not null,
    constraint persons_fk_point_id foreign key (point_id) references points (point_id)
);
comment on column persons.person_id is 'ID of the person';
comment on column persons.name is 'Name of the person';
comment on column persons.age is 'Age of the person';
comment on column persons.gift is 'Gift description';
comment on column persons.donator_id is 'ID of the donator who buys the gift';
comment on column persons.point_id is 'ID of the point person belongs to';

comment on table donators is 'People who are listed in the system waiting for gifts!';
