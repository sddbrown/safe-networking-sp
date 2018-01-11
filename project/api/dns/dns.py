
from elasticsearch_dsl import DocType, Search, Date, Integer, Keyword, Text, Ip, connections, InnerDoc, Nested, Object



class DomainDetailsDoc(DocType):
    name = Text(analyzer='snowball', fields={'raw': Keyword()})
    tags = Keyword()
    doc_created = Date()
    doc_updated = Date()
    processed = Integer()

    class Meta:
        index = 'sfn-domain-details'

    @classmethod
    def get_indexable(cls):
        return cls.get_model().get_objects()

    @classmethod
    def from_obj(cls, obj):
        return cls(
            id=obj.id,
            name=obj.name,
            tags=obj.tags,
            doc_created=obj.doc_created,
            doc_updated=obj.doc_updated,
            processed=obj.processed,
        )

    def save(self, **kwargs):
        return super(DomainDetailsDoc, self).save(**kwargs)


class EventTag(InnerDoc):
    tag_name = Text(fields={'raw': Keyword()})
    public_tag_name = Text(analyzer='snowball')
    tag_class = Text(fields={'raw': Keyword()})
    confidence_level = Integer()
    sample_date = Date()
    file_type = Text(fields={'raw': Keyword()})



class DNSEventDoc(DocType):
    domain_name = Text(analyzer='snowball', fields={'raw': Keyword()})
    device_name = Text(analyzer='snowball', fields={'raw': Keyword()})
    host = Text(analyzer='snowball', fields={'raw': Keyword()})
    threat_id = Text(analyzer='snowball')
    threat_name = Text(analyzer='snowball')
    event_tag = Object(EventTag)
    created_at = Date()
    updated_at = Date()
    processed = Integer()
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
            domain_name=obj.domain_name,
            device_name=obj.device_name,
            host=obj.host,
            threat_id=obj.threat_id,
            event_tag=obj.event_tag,
            created_at=obj.created_at,
            updated_at=obj.updated_at,
            processed=obj.processed,
            src_ip=obj.src_ip,
            dst_ip=obj.dst_ip
        )


    # def addEventTag(self, tag_name, public_tag_name,tag_class,
    #                 confidence_level, sample_date):
    #     self.event_tag.append(
    #         EventTag(tag_name=tag_name, public_tag_name=public_tag_name,
    #                  tag_class=tag_class,confidence_level=confidence_level,
    #                  sample_date=sample_date))
    
    
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
    tag = Keyword()
    doc_created = Date()
    doc_updated = Date()
    processed = Integer()

    class Meta:
        index = 'sfn-tag-details'

    @classmethod
    def get_indexable(cls):
        return cls.get_model().get_objects()

    @classmethod
    def from_obj(cls, obj):
        return cls(
            id=obj.id,
            name=obj.name,
            tag=obj.tag,
            doc_created=obj.doc_created,
            doc_updated=obj.doc_updated,
            processed=obj.processed,
        )

    def save(self, **kwargs):
        return super(TagDetailsDoc, self).save(**kwargs)
