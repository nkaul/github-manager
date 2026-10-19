import unittest
from collections import Counter
from stratify import allocate


class Stratification(unittest.TestCase):
    def test_deterministic_balanced_sampling_buckets_preserve_whole_groups(self):
        groups=[]
        for domain in range(10):
            for i in range(30):
                groups.append([{'numeric_id':domain*60+i*2+j,'sampling_domain':str(domain)} for j in range(2)])
        targets={'development':180,'validation':120,'test_reserved':300}
        assigned, rows, counts, audit=allocate(groups,targets)
        self.assertEqual(counts,targets)
        self.assertEqual(assigned,allocate(list(reversed(groups)),targets)[0])
        for group in groups:
            self.assertEqual(len({assigned[r['numeric_id']]['split'] for r in group}),1)
        for split, target in targets.items():
            self.assertEqual(set(audit['per_domain_actual'][split].values()),{target//10})
        self.assertEqual(Counter(r['split'] for r in rows),{'development':90,'validation':60,'test_reserved':150})


if __name__=='__main__':unittest.main()
