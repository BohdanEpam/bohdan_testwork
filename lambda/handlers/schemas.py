import trafaret as t

AnnouncementsTableSchema = t.Dict(
    {
        t.Key("title"): t.String(),
        t.Key("description"): t.String(),
        t.Key("date"): t.DateTime("%Y-%m-%dT%H:%M:%S.%f%z"),
    },
    ignore_extra=["*"],
)

RequestQueryParamsSchema = t.Dict(
    {
        t.Key("skip", optional=True): t.ToInt(gte=0),
        t.Key("limit", optional=True): t.ToInt(gte=1),
    },
    allow_extra=["*"],
)
