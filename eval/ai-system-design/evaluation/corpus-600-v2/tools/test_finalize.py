import unittest
from finalize import local_targets


class NavigationAudit(unittest.TestCase):
    def test_truncated_source_markdown_is_not_a_local_navigation_target(self):
        text = '''> Source quote: [broken](h…

[Complete README](../../../corpus-600/sources/README.md) · [Full dossier](../../shards/a/record.json) · [Pinned GitHub source](https://github.com/example/repo)

| data | 60 | [data](data.md) |
'''
        self.assertEqual(list(local_targets(text)), ['../../../corpus-600/sources/README.md', '../../shards/a/record.json', 'data.md'])


if __name__=='__main__':unittest.main()
