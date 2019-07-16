from ckan import model
from sqlalchemy import and_, func, select, Table

def table(name):
    return Table(name, model.meta.metadata, autoload=True)

class Stats(object):

    @classmethod
    def top_categories(cls, limit=10):
        member = table('member')
        package = table('package')
        query = select([member.c.group_id, func.count(member.c.table_id)]). \
            group_by(member.c.group_id). \
            where(and_(member.c.group_id != None,
                       member.c.table_name == 'package',
                       member.c.capacity == 'public',
                       member.c.state == 'active',
                       package.c.state == 'active',
                       package.c.private != 'TRUE',
                       package.c.id == member.c.table_id
                       )). \
            order_by(func.count(member.c.table_id).desc()). \
            limit(limit)

        res_ids = model.Session.execute(query).fetchall()
        res_groups = [(model.Session.query(model.Group).get(unicode(group_id)), val) for group_id, val in res_ids]
        return res_groups

    @classmethod
    def top_organisations(cls, limit=10):
        package = table('package')
        query = select([package.c.owner_org, func.count(package.c.owner_org)]). \
            group_by(package.c.owner_org). \
            where(and_(package.c.state == 'active', package.c.private == 'FALSE')). \
            order_by(func.count(package.c.owner_org).desc()). \
            limit(limit)

        res_ids = model.Session.execute(query).fetchall()
        res_groups = [(model.Session.query(model.Group).get(unicode(owner_org)), val) for owner_org, val in res_ids]
        return res_groups

    @classmethod
    def resource_count(cls):
        resource = table('resource')
        package = table('package')
        query = select([func.count(resource.c.id)]). \
            where(and_(resource.c.package_id == package.c.id,
                       resource.c.state == 'active',
                       package.c.state == 'active',
                       # Don't count priv datasets
                       package.c.private != 'TRUE'
                       ))

        res_count = model.Session.execute(query).fetchall()
        return res_count[0][0]

    @classmethod
    def resource_report(cls):
        resource = table('resource')
        group = table('group')
        package = table('package')
        query = select([group.c.title, package.c.title, resource.c.name, resource.c.url, resource.c.created, resource.c.last_modified, resource.c.format, resource.c.webstore_url, resource.c.resource_type]). \
            where(and_(resource.c.package_id == package.c.id,
                       resource.c.state == 'active',
                       group.c.id == package.c.owner_org))

        res_report = model.Session.execute(query).fetchall()
        return res_report

    @classmethod
    def resource_org_count(cls, org_id):
        resource = table('resource')
        package = table('package')
        query = select([func.count(resource.c.id)]). \
            where(and_(resource.c.state == 'active',
                       package.c.state == 'active',
                       resource.c.package_id == package.c.id,
                       package.c.owner_org == org_id,
                       # Don't count priv datasets
                       package.c.private != 'TRUE'
                       ))

        res_count = model.Session.execute(query).fetchall()
        return res_count[0][0]
