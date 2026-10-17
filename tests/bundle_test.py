import io
import json
import os
import tarfile
import tempfile
from hashlib import md5
from unittest import TestCase
from unittest.mock import patch

from modcli import bundle, context
from modcli.http import Response


class PublishTest(TestCase):

    def setUp(self):
        root = tempfile.mkdtemp()
        pkg = os.path.join(root, 'packages', 'my-plugin')
        os.makedirs(os.path.join(pkg, 'src'))
        for name in ('my-plugin.mk', os.path.join('src', 'plugin.c')):
            with open(os.path.join(pkg, name), 'w') as fh:
                fh.write(name)
        self.project_file = os.path.join(root, 'project.json')
        with open(self.project_file, 'w') as fh:
            json.dump({'buildroot_pkg': 'my-plugin', 'bundles': [{'name': 'my-plugin.lv2'}]}, fh)
        self.calls = []

        token = patch.object(context.current_env(), 'token', 'the-token')
        token.start()
        self.addCleanup(token.stop)

    def _post(self, url, data=None, json_data=None, headers=None):
        self.calls.append((url, data, json_data))
        if json_data is not None:
            return Response(200, json.dumps({'id': 'p1', 'source-href': 'https://bundle/p1/source', 'href': 'https://bundle/p1'}))
        return Response(201, f'"{md5(data).hexdigest()}"')

    def test_publish_uploads_the_package(self):
        with patch('modcli.http.post', self._post):
            bundle.publish(self.project_file, None, force=True)

        (_, _, process), (url, source, _) = self.calls
        self.assertEqual(process, {'bundles': [{'name': 'my-plugin.lv2'}], 'rebuild': False})
        self.assertEqual(url, 'https://bundle/p1/source')
        with tarfile.open(fileobj=io.BytesIO(source)) as tar:
            names = {name.rstrip('/') for name in tar.getnames()}
        self.assertLessEqual({'my-plugin/my-plugin.mk', 'my-plugin/src/plugin.c'}, names)
