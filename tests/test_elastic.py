import time
import pytest

from bodspipelines.infrastructure.storage import ElasticStorage
from bodspipelines.mappings.gleif import lei_properties, rr_properties, repex_properties, match_lei, match_rr, match_repex

@pytest.fixture
def elastic_storage():
    return ElasticStorage(indexes={"lei2": {"properties": lei_properties, "match": match_lei},
                                   "rr": {"properties": rr_properties, "match": match_rr},
                                   "repex": {"properties": repex_properties, "match": match_repex}})


@pytest.fixture
def lei_item():
    """Example LEI-CDF v3.1 data"""
    return {'LEI': '097900BICQ0000135514',
          'Entity': {'LegalName': 'Ing. Magdaléna Beňo Frackowiak ZARIA TRAVEL',
                     'TransliteratedOtherEntityNames': ['ING MAGDALENA BENO FRACKOWIAK ZARIA TRAVEL'],
                     'LegalAddress': {'FirstAddressLine': 'Partizánska Ľupča 708', 'City': 'Partizánska Ľupča', 'Country': 'SK', 'PostalCode': '032 15'},
                     'HeadquartersAddress': {'FirstAddressLine': 'Partizánska Ľupča 708', 'City': 'Partizánska Ľupča', 'Country': 'SK', 'PostalCode': '032 15'},
                     'RegistrationAuthority': {'RegistrationAuthorityID': 'RA000670', 'RegistrationAuthorityEntityID': '43846696'},
                     'LegalJurisdiction': 'SK',
                     'EntityCategory': 'SOLE_PROPRIETOR',
                     'LegalForm': {'EntityLegalFormCode': 'C4PZ'},
                     'EntityStatus': 'ACTIVE',
                     'EntityCreationDate': '2007-11-15T08:00:00+01:00'},
          'Registration': {'InitialRegistrationDate': '2018-02-16T00:00:00+01:00',
                           'LastUpdateDate': '2023-01-10T08:30:56.044+01:00',
                           'RegistrationStatus': 'ISSUED',
                           'NextRenewalDate': '2024-02-16T00:00:00+01:00',
                           'ManagingLOU': '097900BEFH0000000217',
                           'ValidationSources': 'FULLY_CORROBORATED',
                           'ValidationAuthority': {'ValidationAuthorityID': 'RA000670', 'ValidationAuthorityEntityID': '43846696'}}}

@pytest.fixture
def rr_item():
    return {'Relationship': {'StartNode': {'NodeID': '213800D716OH3C31TP65', 
                                           'NodeIDType': 'LEI'}, 
                             'EndNode': {'NodeID': '9695003XHGMQG8TRYS42', 
                                         'NodeIDType': 'LEI'}, 
                             'RelationshipType': 'IS_ULTIMATELY_CONSOLIDATED_BY', 
                             'RelationshipPeriods': [{'StartDate': '2014-02-20T00:00:00Z', 
                                                      'EndDate': '2018-08-03T20:10:29.927Z', 
                                                      'PeriodType': 'ACCOUNTING_PERIOD'}, 
                                                     {'StartDate': '2014-02-20T00:00:00Z', 
                                                      'EndDate': '2018-08-03T20:10:29.927Z', 
                                                      'PeriodType': 'RELATIONSHIP_PERIOD'}, 
                                                     {'StartDate': '2014-02-20T00:00:00Z', 
                                                      'EndDate': '2018-08-03T20:10:29.927Z', 
                                                      'PeriodType': 'DOCUMENT_FILING_PERIOD'}], 
                             'RelationshipStatus': 'NULL', 
                             'RelationshipQualifiers': [{'QualifierDimension': 'ACCOUNTING_STANDARD', 
                                                         'QualifierCategory': 'IFRS'}]}, 
            'Registration': {'InitialRegistrationDate': '2014-02-20T00:00:00Z', 
                             'LastUpdateDate': '2018-02-12T12:51:15.563Z', 
                             'RegistrationStatus': 'ANNULLED', 
                             'NextRenewalDate': '2019-02-20T00:00:00Z', 
                             'ManagingLOU': '213800WAVVOPS85N2205', 
                             'ValidationSources': 'FULLY_CORROBORATED', 
                             'ValidationDocuments': 'REGULATORY_FILING', 
                             'ValidationReference': 'https://beta.companieshouse.gov.uk/company/01501275/filing-history/MzE5NDU2NjAzNmFkaXF6a2N4/document?format=pdf&download=0'}}

@pytest.fixture
def repex_item():
    return {'LEI': '2138002UB7RNYRESKE67', 'ExceptionCategory': 'ULTIMATE_ACCOUNTING_CONSOLIDATION_PARENT', 'ExceptionReason': 'NON_CONSOLIDATING'}

def test_create_lei2_index(elastic_storage):
    elastic_storage.setup_indexes()
    indexes = elastic_storage.list_index_details("lei2")
    print(indexes)
    assert indexes['lei2'] == {'mappings': {'dynamic': 'strict', 'properties': {'Entity': {'properties': {'EntityCategory': {'type': 'text'}, 'EntityCreationDate': {'type': 'text'}, 'EntityStatus': {'type': 'text'}, 'HeadquartersAddress': {'properties': {'City': {'type': 'text'}, 'Country': {'type': 'text'}, 'FirstAddressLine': {'type': 'text'}, 'PostalCode': {'type': 'text'}}}, 'LegalAddress': {'properties': {'City': {'type': 'text'}, 'Country': {'type': 'text'}, 'FirstAddressLine': {'type': 'text'}, 'PostalCode': {'type': 'text'}}}, 'LegalForm': {'properties': {'EntityLegalFormCode': {'type': 'text'}}}, 'LegalJurisdiction': {'type': 'text'}, 'LegalName': {'type': 'text'}, 'RegistrationAuthority': {'properties': {'RegistrationAuthorityEntityID': {'type': 'text'}, 'RegistrationAuthorityID': {'type': 'text'}}}, 'TransliteratedOtherEntityNames': {'properties': {'TransliteratedOtherEntityName': {'type': 'text'}}}}}, 'LEI': {'type': 'text'}, 'Registration': {'properties': {'InitialRegistrationDate': {'type': 'text'}, 'LastUpdateDate': {'type': 'text'}, 'ManagingLOU': {'type': 'text'}, 'NextRenewalDate': {'type': 'text'}, 'RegistrationStatus': {'type': 'text'}, 'ValidationAuthority': {'properties': {'ValidationAuthorityEntityID': {'type': 'text'}, 'ValidationAuthorityID': {'type': 'text'}}}, 'ValidationSources': {'type': 'text'}}}}}}


def test_create_rr_index(elastic_storage):
    elastic_storage.setup_indexes()
    indexes = elastic_storage.list_index_details("rr")
    print(indexes)
    assert indexes['rr']['mappings']['properties'] == {'Relationship': {'properties': {'StartNode': {'properties': {'NodeID': {'type': 'text'}, 
                                                                               'NodeIDType': {'type': 'text'}}}, 
                                                  'EndNode': {'properties': {'NodeID': {'type': 'text'}, 
                                                                             'NodeIDType': {'type': 'text'}}}, 
                                                  'RelationshipType': {'type': 'text'}, 
                                                  'RelationshipPeriods': {'properties': {'StartDate': {'type': 'text'}, 
                                                                                         'EndDate': {'type': 'text'}, 
                                                                                         'PeriodType': {'type': 'text'}}}, 
                                                  'RelationshipStatus': {'type': 'text'}, 
                                                  'RelationshipQualifiers': {'properties': {'QualifierDimension': {'type': 'text'}, 
                                                                                            'QualifierCategory': {'type': 'text'}}}}}, 
                  'Registration': {'properties': {'InitialRegistrationDate': {'type': 'text'}, 
                                                  'LastUpdateDate': {'type': 'text'}, 
                                                  'RegistrationStatus': {'type': 'text'}, 
                                                  'NextRenewalDate': {'type': 'text'}, 
                                                  'ManagingLOU': {'type': 'text'}, 
                                                  'ValidationSources': {'type': 'text'}, 
                                                  'ValidationDocuments': {'type': 'text'}, 
                                                  'ValidationReference': {'type': 'text'}}}}


def test_create_repex_index(elastic_storage):
    elastic_storage.setup_indexes()
    indexes = elastic_storage.list_index_details("repex")
    print(indexes)
    assert indexes['repex'] == {'mappings': {'dynamic': 'strict', 
                                             'properties': {'ExceptionCategory': {'type': 'text'}, 
                                                            'ExceptionReason': {'type': 'text'}, 
                                                            'LEI': {'type': 'text'}}}}

def test_write_lei_record(elastic_storage, lei_item):
    item = elastic_storage.process(lei_item, 'lei2')
    #assert item == False
    item = elastic_storage.query('lei2', {"match": {'LEI': '097900BICQ0000135514'}})
    assert item['hits']['hits'][0]['_source'] == lei_item


def test_write_rr_record(elastic_storage, rr_item):
    item = elastic_storage.process(rr_item, 'rr')
    #assert item == False
    item = elastic_storage.query('rr', {"match": {'Registration.ManagingLOU': '213800WAVVOPS85N2205'}})
    #print("Item:", item)
    assert item['hits']['hits'][0]['_source'] == rr_item


def test_write_repex_record(elastic_storage, repex_item):
    item = elastic_storage.process(repex_item, 'repex')
    item = elastic_storage.query('repex', #{'LEI': '2138002UB7RNYRESKE67'})
                   {"bool": {"must": [{"match": {'ExceptionCategory': 'ULTIMATE_ACCOUNTING_CONSOLIDATION_PARENT'}}, 
                                      {"match": {'ExceptionReason': 'NON_CONSOLIDATING'}}, 
                                      {"match": {'LEI': '2138002UB7RNYRESKE67'}}]}})
    assert item['hits']['hits'][0]['_source'] == repex_item

def test_old_record(elastic_storage, lei_item):
    elastic_storage.delete_all("lei2")
    time.sleep(1)
    item = elastic_storage.process(lei_item, "lei2")
    assert item == lei_item
    time.sleep(1)
    item = elastic_storage.process(lei_item, "lei2")
    assert item == False
