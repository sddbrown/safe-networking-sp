
from elasticsearch_dsl import DocType, Search, Date, Integer, Keyword, Text, Ip, connections



class DomainDetailsDoc(DocType):
    name = Text(analyzer='snowball', fields={'raw': Keyword()})
    body = Text(analyzer='snowball')
    tags = Keyword()
    created_at = Date()
    updated_at = Date()
    processed = Integer()
    type_of_doc = Text(analyzer='snowball')

    class Meta:
        index = 'sfn-details'

    @classmethod
    def get_indexable(cls):
        return cls.get_model().get_objects()

    @classmethod
    def from_obj(cls, obj):
        return cls(
            id=obj.id,
            body=obj.body,
            name=obj.name,
            tags=obj.tags,
            created_at=obj.created_at,
            updated_at=obj.updated_at,
            processed=obj.processed,
            type_of_doc=obj.type_of_doc
        )

    def save(self, **kwargs):
        return super(DomainDetailsDoc, self).save(**kwargs)



class DNSEventDoc(DocType):
    domain_name = Text(analyzer='snowball', fields={'raw': Keyword()})
    device_name = Text(analyzer='snowball', fields={'raw': Keyword()})
    host = Text(analyzer='snowball', fields={'raw': Keyword()})
    threat_id = Text(analyzer='snowball')
    threat_name = Text(analyzer='snowball')
    event_tag = Keyword()
    created_at = Date()
    updated_at = Date()
    processed = Integer()
    type_of_doc = Text(analyzer='snowball')
    src_ip = Ip()
    dst_ip = Ip()

    class Meta:
        index = 'sfn-dns-event'

    @classmethod
    def get_indexable(cls):
        return cls.get_model().get_objects()

    @classmethod
    def from_obj(cls, obj):
        return cls(
            id=obj.id,
            title=obj.title,
            tags=obj.tags,
            created_at=obj.created_at,
            updated_at=obj.updated_at,
            processed=obj.processed,
            type_of_doc=obj.type_of_doc
        )

    def save(self, **kwargs):
        return super(DNSEventDoc, self).save(**kwargs)



class AFDetailsDoc(DocType):    
    daily_points = Integer()
    daily_points_remaining = Integer()
    minute_points = Integer()
    minute_points_remaining = Integer()
    minute_bucket_start = Date()
    daily_bucket_start = Date()
        

    class Meta:
        index = 'af-details'
        id = 'af-details'

    @classmethod
    def get_indexable(cls):
        return cls.get_model().get_objects()

    @classmethod
    def from_obj(cls, obj):
        return cls(
            id=obj.id,
            daily_points=obj.daily_points,
            daily_points_remaining=obj.daily_points_remaining,
            minute_points=obj.minute_points,
            minute_points_remaining=obj.minute_points_remaining,
            daily_bucket_start=obj.daily_bucket_start,
            minute_bucket_start=obj.minute_bucket_start
        )

    def save(self, **kwargs):
        return super(AFDetailsDoc, self).save(**kwargs)



class TagDetailsDoc(DocType):
    name = Text(analyzer='snowball', fields={'raw': Keyword()})
    body = Text(analyzer='snowball')
    tag = Keyword()
    created_at = Date()
    updated_at = Date()
    processed = Integer()
    type_of_doc = Text(analyzer='snowball')

    class Meta:
        index = 'sfn-details'

    @classmethod
    def get_indexable(cls):
        return cls.get_model().get_objects()

    @classmethod
    def from_obj(cls, obj):
        return cls(
            id=obj.id,
            body=obj.body,
            name=obj.name,
            tag=obj.tags,
            created_at=obj.created_at,
            updated_at=obj.updated_at,
            processed=obj.processed,
            type_of_doc=obj.type_of_doc
        )

    def save(self, **kwargs):
        return super(TagDetailsDoc, self).save(**kwargs)
