"""
Tests - Deuce Client - API - Vault - Serialize
"""
from unittest import TestCase

import deuceclient.api as api
import deuceclient.common.errors as errors
import deuceclient.common.validation as val
from deuceclient.tests import *


class VaultTest(TestCase):

    def setUp(self):
        super(VaultTest, self).setUp()

        self.vault_id = create_vault_name()
        self.project_id = create_project_name()

    def check_block_instance(self, a, b):
        self.assertEqual(a.project_id, b.project_id)
        self.assertEqual(a.vault_id, b.vault_id)
        if a.block_id is None:
            self.assertIsNone(b.block_id)
        else:
            self.assertEqual(a.block_id, b.block_id)
        if a.storage_id is None:
            self.assertIsNone(b.storage_id)
        else:
            self.assertEqual(a.storage_id, b.storage_id)
        self.assertEqual(a.ref_count, b.ref_count)
        self.assertEqual(a.ref_modified, b.ref_modified)
        self.assertEqual(a.block_size, b.block_size)
        self.assertEqual(a.block_orphaned, b.block_orphaned)
        self.assertEqual(a.block_type, b.block_type)

        # Note: Cannot check length as block data is not transferred
        #       and len(Block) requires the data be present

    def check_blocks(self, a, b):
        self.assertEqual(a.project_id, b.project_id)
        self.assertEqual(a.vault_id, b.vault_id)
        self.assertEqual(a.marker, b.marker)
        self.assertEqual(len(a), len(b))
        for k, v in a.items():
            self.assertIn(k, b)
            self.check_block_instance(v, b[k])
        for k, v in b.items():
            self.assertIn(k, a)
            self.check_block_instance(v, a[k])

    def check_file_instance(self, a, b):
        self.assertEqual(a.project_id, b.project_id)
        self.assertEqual(a.vault_id, b.vault_id)
        self.assertEqual(a.file_id, b.file_id)
        self.assertEqual(a.url, b.url)
        self.assertEqual(a._File__properties['maximum_offset'],
                         b._File__properties['maximum_offset'])
        self.check_blocks(a.blocks, b.blocks)
        self.assertEqual(len(a), len(b))
        for k, v in a.offsets.items():
            self.assertIn(k, b.offsets)
            self.assertEqual(v, b[k])

        for k, v in b.offsets.items():
            self.assertIn(k, a.offsets)
            self.assertEqual(v, a[k])

    def check_files(self, a, b):
        self.assertEqual(a.project_id, b.project_id)
        self.assertEqual(a.vault_id, b.vault_id)
        self.assertEqual(a.marker, b.marker)
        self.assertEqual(len(a), len(b))

        # Ensure everything in 'a' is in 'b'
        for k, v in a.items():
            self.assertIn(k, b)
            self.check_file_instance(v, b[k])
        # Ensure the reverse as well just in case
        for k, v in b.items():
            self.assertIn(k, a)
            self.check_file_instance(v, a[k])

    def check_vault(self, a, b):
        self.assertEqual(a.project_id, b.project_id)
        self.assertEqual(a.vault_id, b.vault_id)
        self.check_blocks(a.blocks, b.blocks)
        self.check_blocks(a.storageblocks, b.storageblocks)
        self.check_files(a.files, b.files)

    def test_json_serialize_block(self):
        block_info = create_block()
        block = api.Block(self.project_id,
                          self.vault_id,
                          block_id=block_info[0],
                          data=block_info[1],
                          block_size=block_info[2])

        json_data = block.to_json()

        new_block = api.Block.from_json(json_data)

        self.check_block_instance(block, new_block)

    def test_json_serialize_file(self):
        a_file = api.File(self.project_id,
                          self.vault_id,
                          create_file())
        json_data = a_file.to_json()

        new_file = api.File.from_json(json_data)

        self.check_file_instance(a_file, new_file)

    def test_json_serialize_blocks(self):
        blocks = api.Blocks(self.project_id,
                            self.vault_id)
        blocks.update({
            block[0]: api.Block(self.project_id,
                                self.vault_id,
                                block_id=block[0],
                                data=block[1],
                                block_size=block[2])
            for block in create_blocks(block_count=10)
        })

        json_data = blocks.to_json()

        new_blocks = api.Blocks.from_json(json_data)

        self.check_blocks(blocks, new_blocks)

    def test_json_serialize_storage_blocks(self):
        storageblocks = api.StorageBlocks(self.project_id,
                                          self.vault_id)
        json_data = storageblocks.to_json()

        new_storageblocks = api.StorageBlocks.from_json(json_data)

        self.check_blocks(storageblocks, new_storageblocks)

    def test_json_serialize_files_blocks(self):
        files = api.Files(self.project_id,
                          self.vault_id)
        files.update({
            file_id: api.File(self.project_id,
                              self.vault_id,
                              file_id)
            for file_id in [create_file() for _ in range(10)]
        })

        json_data = files.to_json()

        new_files = api.Files.from_json(json_data)

        self.check_files(files, new_files)

    def test_json_serialize(self):
        vault = api.Vault(self.project_id,
                          self.vault_id)

        json_data = vault.to_json()

        new_vault = api.Vault.from_json(json_data)
        self.check_vault(vault, new_vault)

    def test_json_serialize_with_data(self):
        vault = api.Vault(self.project_id,
                          self.vault_id)

        vault.blocks.update({
            block[0]: api.Block(self.project_id,
                                self.vault_id,
                                block_id=block[0],
                                data=block[1],
                                block_size=block[2])
            for block in create_blocks(block_count=10)
        })
        vault.files.update({
            file_id: api.File(self.project_id,
                              self.vault_id,
                              file_id)
            for file_id in [create_file() for _ in range(10)]
        })

        json_data = vault.to_json()

        new_vault = api.Vault.from_json(json_data)

        self.check_vault(vault, new_vault)
