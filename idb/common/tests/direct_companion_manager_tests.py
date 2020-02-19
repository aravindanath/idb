#!/usr/bin/env python3
# Copyright (c) Facebook, Inc. and its affiliates.
#
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

import json
import tempfile
from pathlib import Path
from unittest import mock

from idb.common.direct_companion_manager import DirectCompanionManager
from idb.common.format import json_data_companions, json_to_companion_info
from idb.common.types import Address, CompanionInfo
from idb.utils.testing import TestCase, ignoreTaskLeaks


@ignoreTaskLeaks
class CompanionManagerTests(TestCase):
    async def test_add_companion(self) -> None:
        with tempfile.NamedTemporaryFile() as f:
            with open(f.name, "w") as temp:
                json.dump(json_data_companions([]), temp)
            companion_manager = DirectCompanionManager(
                logger=mock.MagicMock(), state_file_path=f.name
            )
            companion = CompanionInfo(
                udid="asdasda", host="foohost", port=123, is_local=False
            )
            await companion_manager.add_companion(companion)
            data = json.load(f)
            companions = json_to_companion_info(data)
            read_companion: CompanionInfo = companions[0]
            self.assertEqual(companion, read_companion)

    async def test_get_companions(self) -> None:
        with tempfile.NamedTemporaryFile() as f:
            companion_manager = DirectCompanionManager(
                logger=mock.MagicMock(), state_file_path=f.name
            )
            companion = CompanionInfo(
                udid="asdasda", host="foohost", port=123, is_local=False
            )
            with open(f.name, "w") as f:
                json.dump(json_data_companions([companion]), f)
            companions = await companion_manager.get_companions()
            read_companion: CompanionInfo = companions[0]
            self.assertEqual(companion, read_companion)

    async def test_clear(self) -> None:
        with tempfile.NamedTemporaryFile() as f:
            with open(f.name, "w") as temp:
                json.dump(json_data_companions([]), temp)
            companion_manager = DirectCompanionManager(
                logger=mock.MagicMock(), state_file_path=f.name
            )
            companion = CompanionInfo(
                udid="asdasda", host="foohost", port=123, is_local=False
            )
            await companion_manager.add_companion(companion)
            await companion_manager.clear()
            companions = await companion_manager.get_companions()
            self.assertEqual(companions, [])

    async def test_remove_companion_with_udid(self) -> None:
        with tempfile.NamedTemporaryFile() as f:
            companion_manager = DirectCompanionManager(
                logger=mock.MagicMock(), state_file_path=f.name
            )
            companion = CompanionInfo(
                udid="asdasda", host="foohost", port=123, is_local=False
            )
            with open(f.name, "w") as f:
                json.dump(json_data_companions([companion]), f)
            await companion_manager.remove_companion(
                Address(host=companion.host, port=companion.port)
            )
            companions = await companion_manager.get_companions()
            self.assertEqual(companions, [])

    async def test_remove_companion_with_host_and_port(self) -> None:
        with tempfile.NamedTemporaryFile() as f:
            companion_manager = DirectCompanionManager(
                logger=mock.MagicMock(), state_file_path=f.name
            )
            companion = CompanionInfo(
                udid="asdasda", host="foohost", port=123, is_local=False
            )
            with open(f.name, "w") as f:
                json.dump(json_data_companions([companion]), f)
            await companion_manager.remove_companion(companion.udid)
            companions = await companion_manager.get_companions()
            self.assertEqual(companions, [])

    async def test_compound_behaviour_on_absent_state_file(self) -> None:
        with tempfile.TemporaryDirectory() as dir:
            companion_manager = DirectCompanionManager(
                logger=mock.MagicMock(), state_file_path=str(Path(dir) / "state_file")
            )
            companions = await companion_manager.get_companions()
            self.assertEqual(companions, [])
            companion = CompanionInfo(
                udid="asdasda", host="foohost", port=123, is_local=False
            )
            await companion_manager.add_companion(companion)
            companions = await companion_manager.get_companions()
            self.assertEqual(companions, [companion])
