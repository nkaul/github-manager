"""Offline corpus invariants; generated expectations stay separate from app inputs."""
import json
import hashlib
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

import assemble


class AssemblySafety(unittest.TestCase):
    def test_raw_crlf_quote_coordinates_are_preserved(self):
        with tempfile.TemporaryDirectory() as d,patch.object(assemble,'ROOT',Path(d)),patch.object(assemble,'DATA',Path(d)/'data'):
            raw=b'Heading\r\nPurpose line\r\nMore evidence\r\n';p=Path(d)/'data/sources/1/commit/README.md';p.parent.mkdir(parents=True);p.write_bytes(raw)
            source={'path':'README.md','local_path':str(p.relative_to(Path(d))),'bytes':len(raw),'sha256':hashlib.sha256(raw).hexdigest(),
                    'git_blob_sha':hashlib.sha1(f'blob {len(raw)}\0'.encode()+raw).hexdigest(),'role':'README'}
            record={'numeric_id':1,'private':False,'source':'PUBLIC_GITHUB','commit':'commit','readme':source,'supporting_files':[],
                    'annotations':{'topics':[{'evidence':[{'path':'README.md','start_line':2,'end_line':3,'quote':'Purpose line\r\nMore evidence'}]}]}}
            self.assertEqual(assemble.audit_sources([record])['issues'],[])

    def test_kind_and_technology_ids_remain_distinct(self):
        ids={assemble.concept_id('TAG',n) for n in ['C','C++','C#']}
        self.assertEqual(len(ids),3)
        self.assertNotEqual(assemble.concept_id('PROJECT','PyTorch'),assemble.concept_id('TAG','PyTorch'))

    def test_annotation_and_search_data_do_not_enter_app_input(self):
        r={'numeric_id':1,'full_name':'o/r','description':'public description','native_topics':['native'],
           'primary_language':'Python','readme':{'git_blob_sha':'a'*40,'local_path':'source/README.md'},
           'annotations':{'purpose':'REFERENCE_ONLY_MARKER','projects':[],'topics':[],'tags':[]},
           'discovery':{'query':'SECRET_EXPECTATION_MARKER'},'record_path':'dossier.json'}
        inputs,labels=assemble.inputs_and_labels([r],{}, {}, {})
        self.assertNotIn('REFERENCE_ONLY_MARKER',json.dumps(inputs))
        self.assertNotIn('SECRET_EXPECTATION_MARKER',json.dumps(inputs))
        self.assertEqual(labels[0]['purpose'],'REFERENCE_ONLY_MARKER')
        self.assertFalse(labels[0]['human_approved'])
        self.assertEqual(labels[0]['dimension_status']['unlisted_memberships'],'UNKNOWN_NOT_NEGATIVE')

    def test_stale_or_same_author_review_cannot_approve_reference(self):
        with tempfile.TemporaryDirectory() as d,patch.object(assemble,'ROOT',Path(d)),patch.object(assemble,'DATA',Path(d)/'data'):
            record={'numeric_id':1,'collector_agent':'a','annotations':{'purpose':'current'},'readme':{'sha256':'source'}}
            labels=[{'repository_id':1,'status':'PROPOSED','human_approved':False}]
            folder=Path(d)/'data/cross-review/b';folder.mkdir(parents=True)
            review={'repository_id':1,'reviewer':'b','annotation_sha256':assemble.digest({'purpose':'old'}),'readme_sha256':'source',
                    'verdict':'SUPPORTED','inspected_sources':[{'path':'README.md','line_intervals':[[1,2]]}]}
            (folder/'results.local.json').write_text(json.dumps([review]))
            result=assemble.attach_cross_reviews([record],labels)
            self.assertEqual(result['valid_reviews'],0);self.assertEqual(labels[0]['status'],'PROPOSED')
            review['annotation_sha256']=assemble.digest(record['annotations']);review['reviewer']='a'
            (folder/'results.local.json').write_text(json.dumps([review]))
            self.assertEqual(assemble.attach_cross_reviews([record],labels)['valid_reviews'],0)
            review['reviewer']='b';(folder/'results.local.json').write_text(json.dumps([review]))
            self.assertEqual(assemble.attach_cross_reviews([record],labels)['valid_reviews'],1)
            self.assertEqual(labels[0]['status'],'CROSS_REVIEWED');self.assertFalse(labels[0]['human_approved'])


if __name__=='__main__':unittest.main()
