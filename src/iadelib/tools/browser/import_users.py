# -*- coding: utf-8 -*-
from AccessControl import Unauthorized
from plone import api
import csv
from Products.CMFPlone.utils import normalizeString
from Products.CMFCore.exceptions import BadRequest
from Products.CMFPlone.utils import safe_unicode
from Products.Five import BrowserView
from Products.CMFCore.utils import getToolByName

PLONEGROUP_ORG = 'plonegroup-organization'
DEFAULT_DIRECTORY_ID = 'contacts'


class ImportUsers(BrowserView):

    def get_plone_group_id(self, prefix, suffix):
        """
            Return Plone group id corresponding to prefix/suffix.
        """
        # make sure we received an str as org_uid, not an org
        if not isinstance(prefix, (str, unicode)):
            raise TypeError('Parameter prefix must be str or unicode instance!')
        return '{0}_{1}'.format(prefix, suffix)

    def get_own_organization(self, default=True):
        """
            get plonegroup-organization object
            If p_default is True, we get it in a "contacts" directory added to the portal root.
        """
        if default:
            portal = api.portal.get()
            return portal.get(DEFAULT_DIRECTORY_ID).get(PLONEGROUP_ORG)
        else:
            catalog = api.portal.get_tool('portal_catalog')
            brains = catalog(portal_type='organization', id=PLONEGROUP_ORG)
            if brains:
                return brains[0].getObject()

    def org_id_to_uid(self, org_info, raise_on_error=True):
        """Returns the corresponding org based value for given org_info based value.
           'developers', will return 'orguid'.
           'developers_creators' will return 'orguid_creators'."""
        own_org = self.get_own_organization()
        try:
            if '_' in org_info:
                org_path, suffix = org_info.split('_')
                org = own_org.restrictedTraverse(org_path.encode('utf-8'))
                return self.get_plone_group_id(org.UID(), suffix)
            else:
                org = own_org.restrictedTraverse(org_info.encode('utf-8'))
                return org.UID()
        except Exception, exc:
            if raise_on_error:
                return None

    def import_user_from_csv(self, fname=None):
        """
          Import the users and attribute roles from the 'csv file' (fname received as parameter)
        """

        member = api.user.get_current()
        if not member.has_role('Manager'):
            raise Unauthorized('You must be a Manager to access this script !')

        if not fname:
            return "This script needs a 'fname' parameter"

        try:
            file = open(fname, "rb")
            reader = csv.DictReader(file)
        except Exception, msg:
            file.close()
            return "Error with file : %s" % msg.value

        out = []

        acl = getToolByName(self, 'acl_users')
        pms = api.portal.get_tool('portal_membership')
        pgr = api.portal.get_tool('portal_groups')
        registration = api.portal.get_tool('portal_registration')
        for row in reader:
            row_id = normalizeString(row['username'], self)
            # add users if not exist
            if row_id not in [ud['userid'] for ud in acl.searchUsers()]:
                try:
                    pms.addMember(row_id, row['password'], ('Member',), [])
                    member = pms.getMemberById(row_id)
                    properties = {'fullname': row['fullname'], 'email': row['email']}
                    failMessage = registration.testPropertiesValidity(properties, member)
                    if failMessage is not None:
                        raise BadRequest(failMessage)
                    member.setMemberProperties(properties)
                    out.append("User '%s' is added" % row_id)
                except:
                    import pdb;pdb.set_trace()
            else:
                out.append("User %s already exists" % row_id)
            # attribute roles
            group_title = safe_unicode(row['grouptitle'])
            org_id = normalizeString(group_title, self)
            org_uid = self.org_id_to_uid(org_id)
            plone_groups = []
            if org_uid:
                if row['observers']:
                    plone_groups.append(org_uid + '_observers')
                if row['creators']:
                    plone_groups.append(org_uid + '_creators')
                if row['reviewers']:
                    plone_groups.append(org_uid + '_reviewers')
                if row['advisers']:
                    plone_groups.append(org_uid + '_advisers')
            if row['so']:
                plone_groups.append(group_title + '_powerobservers')
            if row['sor']:
                plone_groups.append(group_title + '_restrictedpowerobservers')
            if row['gs']:
                plone_groups.append(group_title + '_meetingmanagers')

            for plone_group_id in plone_groups:
                pgr.addPrincipalToGroup(row_id, plone_group_id)
                out.append("    -> Added in group '%s'" % plone_group_id)


        file.close()

        return '\n'.join(out)