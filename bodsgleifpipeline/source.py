from bodspipelines.infrastructure.utils import build_date, current_date_iso
from bodspipelines.infrastructure.schemes.data import get_scheme
from .codelists.data import load_data, search_data

def relationship_type(item):
    rtype = item["Relationship"]["RelationshipType"]
    if rtype == "IS_ULTIMATELY_CONSOLIDATED_BY":
        return "U"
    elif rtype == "IS_DIRECTLY_CONSOLIDATED_BY":
        return "D"
    else:
        return "O"

def exception_type(item):
    etype = item["ExceptionCategory"]
    if etype == "ULTIMATE_ACCOUNTING_CONSOLIDATION_PARENT":
        return "U"
    elif etype == "DIRECT_ACCOUNTING_CONSOLIDATION_PARENT":
        return "D"

def exception_unspecified(item):
    if item['ExceptionReason'] == 'NO_LEI':
        return {"reason":"interestedPartyExemptFromDisclosure","description":"Exception Reason: NO_LEI. This parent legal entity does not consent to obtain an LEI or to authorize its child entity to obtain an LEI on its behalf."}
    elif item['ExceptionReason'] == 'NATURAL_PERSONS':
        return {"reason":"interestedPartyExemptFromDisclosure","description":"Exception Reason: NATURAL_PERSONS. The entity is controlled by a natural person(s) without any intermediate legal entity."}
    elif item['ExceptionReason'] == 'NON_CONSOLIDATING':
        return {"reason":"interestedPartyExemptFromDisclosure","description":"Exception Reason: NON_CONSOLIDATING. The legal entity or entities are not obliged to provide consolidated accounts in relation to the entity they control."}
    elif item['ExceptionReason'] == 'NO_KNOWN_PERSON':
        return {"reason":"informationUnknownToPublisher","description":"Exception Reason: NO KNOWN_PERSON. There is no known person(s) controlling the entity."}
    elif item['ExceptionReason'] == 'NON_PUBLIC':
        return {"reason":"interestedPartyExemptFromDisclosure","description":"Exception Reason: NON_PUBLIC. Information about the relationship with the controlling entity is not public."}

#def get_scheme(scheme_id, scheme_data):
#    match = [scheme for scheme in scheme_data if scheme[0] == scheme_id]
#    if match:
#        country = match[0][2]
#        return lookup_scheme(country, "company")
#    return None, None

class GLEIFSource():
    """GLEIF specific methods"""
    def __init__(self):
        self.scheme_data = load_data("2022-03-23_ra_list_v1.7.csv")
        self.legal_forms = load_data("2023-09-28-elf-code-list-v1.5.csv")

    def identify_item(self, item):
        """Identify type of GLEIF data"""
        #print("Item:", item)
        if 'Entity' in item:
            return 'entity'
        elif 'Relationship' in item:
            return 'relationship'
        elif 'ExceptionCategory' in item:
            return 'exception'

    def skip_item(self, item):
        return False

    def record_id(self, item, item_type):
        """recordId for GLEIF item"""
        item_type = self.identify_item(item)
        if item_type == 'entity':
            return f"XI-LEI-{item['LEI']}"
        elif item_type == 'relationship':
            start = item["Relationship"]["StartNode"]['NodeID']
            end = item["Relationship"]["EndNode"]['NodeID']
            rtype = relationship_type(item)
            return f"XI-LEI-RR-{rtype}-{start}-{end}"
        elif item_type == 'exception':
            start = item["LEI"]
            etype = exception_type(item)
            return f"XI-LEI-RE-{etype}-{start}"

    def relationship_id(self, item):
        """Identifier for GLEIF relationship"""
        if "Relationship" in item:
            start = item["Relationship"]["StartNode"]['NodeID']
            rtype = relationship_type(item)
            return f"XI-LEI-RR-{rtype}-{start}"
        else:
            start = item["LEI"]
            rtype = exception_type(item)
            return f"XI-LEI-RR-{rtype}-{start}"

    def exception_id(self, record_id):
        """Relationship coresponding recordId for exception"""
        #return record_id.replace('-RR-', '-RE-')
        return record_id.rsplit("-", 1)[0].replace("-RR-", "-RE-")

    def declaration_subject(self, item):
        """declarationSubject for GLEIF item"""
        item_type = self.identify_item(item)
        if item_type == 'entity':
            return f"XI-LEI-{item['LEI']}"
        elif item_type == 'relationship':
            start = item["Relationship"]["StartNode"]['NodeID']
            return f"XI-LEI-{start}"
        elif item_type == 'exception':
            return f"XI-LEI-{item['LEI']}"

    def item_updated(self, item):
        """statementDate for GLEIF item"""
        #item_type = self.identify_item(item)
        #if item_type == 'entity':
        #    return item["Registration"]["LastUpdateDate"]
        #elif item_type == 'relationship':
        #    return item["Registration"]["LastUpdateDate"]
        #elif item_type == 'exception':
        return item["ContentDate"]

    def item_closed(self, item, item_type):
        """Is GLEIF item closed?"""
        #item_type = self.identify_item(item)
        #print(item)
        if item_type == 'entity':
            return item["Registration"]["RegistrationStatus"] in ('RETIRED', 'DUPLICATE', 'ANNULLED')
        elif item_type == 'relationship':
            #print("item_closed:", item)
            if 'Relationship' in item:
                if "Extension" in item and "Deletion" in item["Extension"]:
                    return True
                return item["Registration"]["RegistrationStatus"] in ('RETIRED', 'DUPLICATE', 'ANNULLED')
            else:
                return True if "Extension" in item and "Deletion" in item["Extension"] else False
        #elif item_type == 'exception':
        #    return True if "Extension" in item and "Deletion" in item["Extension"] else False

    def name(self, item, item_type):
        """Name for GLEIF item"""
        return item['Entity']['LegalName']

    def alternate_names(self, item, item_type):
        """List alternate names"""
        names = []
        if "OtherEntityNames" in item['Entity']:
            for name in item['Entity']["OtherEntityNames"]:
                if "OtherEntityName" in name and name["OtherEntityName"]:
                    names.append(name["OtherEntityName"])
        return names

    def jurisdiction(self, item):
        return item['Entity']['LegalJurisdiction']

    def scheme(self, item, item_type) -> str:
        """Get scheme"""
        if item_type == "entity":
            return 'XI-LEI', 'Global Legal Entity Identifier Index', "https://www.gleif.org/en/about-lei/introducing-the-legal-entity-identifier-lei"

    #@property
    #def scheme_name(self) -> str:
    #    """Get scheme name"""
    #    return 'Global Legal Entity Identifier Index'

    #def scheme_url(self, item):
    #    """Scheme url"""
    #    return "https://www.gleif.org/en/about-lei/introducing-the-legal-entity-identifier-lei"

    def identifier(self, item, item_type) -> str:
        """Get entity identifier"""
        if item_type == "entity":
            return item['LEI']

    def additional_identifiers(self, item) -> list:
        """Get list of additional identifiers"""
        if ("RegistrationAuthority" in item['Entity']
            and "RegistrationAuthorityID" in item['Entity']["RegistrationAuthority"]
            and "RegistrationAuthorityEntityID" in item['Entity']["RegistrationAuthority"]):
            authority = item['Entity']["RegistrationAuthority"]
            scheme_code, scheme_name, scheme_url = get_scheme(authority["RegistrationAuthorityID"],
                                                  self.scheme_data,
                                                  country_code=item['Entity']['LegalJurisdiction'])
            #print(authority, scheme_code, scheme_name)
            identifier = {'id': authority["RegistrationAuthorityEntityID"],
                          'scheme': scheme_code,
                          'schemeName': scheme_name}
            if scheme_url: identifier['uri'] = scheme_url
            return [identifier]
        else:
            return []

    def creation_date(self, item):
        """Creation date for GLEIF item"""
        if "EntityCreationDate" in item['Entity']:
            return item['Entity']["EntityCreationDate"]
        else:
            return None

    def dissolution_date(self, item):
        """Dissolution date for item"""
        if "LegalEntityEvents" in item['Entity']:
            for event in item['Entity']["LegalEntityEvents"]:
                if (event["LegalEntityEventType"] == "DISSOLUTION" and
                    "LegalEntityEventEffectiveDate" in event):
                         return build_date(event["LegalEntityEventEffectiveDate"])
            return None
        else:
            return None

    def _extract_address(self, address, data):
        #print("Data:", data)
        if 'FirstAddressLine' in data:
            address['address1'] = data['FirstAddressLine']
        if 'AdditionalAddressLine' in data:
            address['address2'] = data['AdditionalAddressLine']
        if 'City' in data:
            address['city'] = data['City']
        if 'PostalCode' in data:
            address['postcode'] = data['PostalCode']
        if 'Region' in data:
            address['region'] = data['Region']
        if 'Country' in data:
            address['country'] = data['Country']

    def registered_address(self, item) -> dict:
        """Get registered address"""
        address = {}
        #print("Data:", item)
        if 'LegalAddress' in item['Entity']:
            self._extract_address(address, item['Entity']['LegalAddress'])
        return address

    def business_address(self, item) -> dict:
        """Get registered address"""
        address = {}
        #print("Data:", item)
        if 'HeadquartersAddress' in item['Entity']:
            self._extract_address(address, item['Entity']['HeadquartersAddress'])
        return address

    def relationship_subject(self, item) -> dict:
        """Get relationship subject"""
        item_type = self.identify_item(item)
        if item_type == "relationship":
            return f"XI-LEI-{item['Relationship']['StartNode']['NodeID']}"
        else:
            return f"XI-LEI-{item['LEI']}"

    def create_interested_party(self, item):
        """Create interested party"""
        return None

    def relationship_interested_party(self, item) -> dict:
        """Get relationship subject"""
        item_type = self.identify_item(item)
        if item_type == "relationship":
            return f"XI-LEI-{item['Relationship']['EndNode']['NodeID']}"
        else:
            return exception_unspecified(item)

    def interest_start_date(self, item) -> dict:
        """Get interest start date"""
        start_date = False
        interestStartDate = False
        if 'RelationshipPeriods' in item['Relationship']:
            periods = item['Relationship']['RelationshipPeriods']
            for period in periods:
                if 'StartDate' in period and 'PeriodType' in period:
                    if period['PeriodType'] == "RELATIONSHIP_PERIOD":
                        interestStartDate = period['StartDate']
                    else:
                        start_date = period['StartDate']
        if not start_date:
            if not interestStartDate: interestStartDate = ""
        else:
            if not interestStartDate: interestStartDate = start_date
        return interestStartDate.split("T")[0] if interestStartDate else ""

    def _interest_level(self, item, default):
        """Calculate interest level"""
        relationship_type = item['Relationship']['RelationshipType']
        if relationship_type == "IS_ULTIMATELY_CONSOLIDATED_BY":
            return "indirect"
        elif relationship_type in ("IS_DIRECTLY_CONSOLIDATED_BY", "IS_INTERNATIONAL_BRANCH_OF",
                                   "IS_FUND-MANAGED_BY", "IS_SUBFUND_OF", "IS_FEEDER_TO"):
            return "direct"
        else:
            return default # Other options in data

    def interest_level(self, item):
        """Get interest level"""
        #interestLevel = self._interest_level(item, 'unknown')
        interestLevel = "unknown"
        return interestLevel

    def interest_types(self, item):
        """Get interest types"""
        return {"otherInfluenceOrControl": {"maximum": None,
                      "minimum": None,
                      "exclusiveMinimum": None,
                      "exclusiveMaximum": None}}

    def interest_details(self, item):
        """Get interest details"""
        item_type = self.identify_item(item)
        if item_type == "relationship":
            return f"Relationship Type: {item['Relationship']['RelationshipType']}"
        else:
            return f"Exception Category: {item['ExceptionCategory']}"

    def source_type(self, item) -> str:
        """Get source type"""
        item_type = self.identify_item(item)
        if item_type == "entity":
            return (['officialRegister', 'verified'] if 'ValidationSources' in item['Registration']
                  and item['Registration']['ValidationSources'] ==
                 'FULLY_CORROBORATED' else ['officialRegister'])
        else:
            return ['officialRegister']

    @property
    def source_description(self) -> str:
        """Get source description"""
        return {'name': 'GLEIF', 'uri': 'https://www.gleif.org'}

    @property
    def source_url(self) -> str:
        """Get source url"""
        return 'https://www.gleif.org/en/lei-data/gleif-golden-copy/download-the-golden-copy'

    @property
    def entity_name(self) -> str:
        """Get GLEIF entity name"""
        return 'LEI'

    def entity_status(self, item) -> str:
        """Get GLEIF entity status"""
        return None #item['Entity']['EntityStatus']

    def registration_status(self, item) -> str:
        """Get GLEIF registration status"""
        return item["Registration"]["RegistrationStatus"]

    def item_link(self, item, item_type):
        """Link to more info on entity"""
        if item_type == "entity":
            if "LEI" in item and item["LEI"]:
                return f'https://search.gleif.org/#/record/{item["LEI"]}'
            else:
                return None
        else:
            return None

    def retrived_date(self, item):
        """Date that data was retrieve"""
        if "ContentDate" in item:
            return item["ContentDate"].split("T")[0]
        else:
            return current_date_iso()

    def entity_details(self, item):
        """Link to more info on entity"""
        if 'LegalForm' in item['Entity'] and 'EntityLegalFormCode' in item['Entity']['LegalForm']:
            legal_form = search_data(self.legal_forms, 0, item['Entity']['LegalForm']['EntityLegalFormCode'])
            if legal_form[5]:
                return legal_form[5]
        return None

    def has_public_listing(self, item):
        """Does entity have public listing"""
        return None
