import json
import sys
from pathlib import Path

import cv2
import numpy as np
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import chalk
import parallax
import studio


def figure_scene():
    h, w = 240, 160
    layer = np.zeros((h, w, 3), np.float32)
    layer[40:200, 30:130] = 0.3
    mask = np.zeros((h, w), np.float32)
    mask[80:200, 60:100] = 1.0
    layer[80:200, 60:100] = 0.9
    return layer, mask


def test_scene_mode_defaults_and_validation():
    script = {"scenes": []}
    assert parallax.scene_mode(script, {}) == "off"
    assert parallax.scene_mode({"depth": "mask"}, {}) == "mask"
    assert parallax.scene_mode({"depth": "mask"}, {"depth": "off"}) == "off"
    assert parallax.scene_mode(script, {"kind": "verse", "depth": "depth"}) == "off"
    with pytest.raises(ValueError):
        parallax.scene_mode(script, {"depth": "deep"})
    assert parallax.wants_mask(script, {"alive": True})
    assert not parallax.wants_mask(script, {})


def test_plane_cams_start_at_base_camera():
    layer, mask = figure_scene()
    planes = parallax.build_planes(layer, mask)
    cam = (1.05, 80.0, 120.0, 1.0, -2.0, 0.0)
    cams = parallax.plane_cams(cam, (80.0, 120.0), planes, 0.0)
    assert all(np.allclose(c, cam) for c in cams)
    later = parallax.plane_cams(cam, (80.0, 120.0), planes, 1.0)
    assert later[1][0] > cam[0] and later[1][3] != cam[3]


def test_composite_identity_matches_single_warp_outside_figure():
    layer, mask = figure_scene()
    planes = parallax.build_planes(layer, mask)
    M = np.float32([[1, 0, 0], [0, 1, 0]])
    out = parallax.composite(layer, planes, [M, M], (160, 240))
    assert np.allclose(out[mask[..., None].repeat(3, 2) > 0.99], 0.9, atol=2e-3)
    assert np.allclose(out[:30], layer[:30], atol=1e-5)


def test_composite_moves_figure_and_fills_gap():
    layer, mask = figure_scene()
    planes = parallax.build_planes(layer, mask)
    M = np.float32([[1, 0, 0], [0, 1, 0]])
    Mn = np.float32([[1, 0, 12], [0, 1, 0]])
    out = parallax.composite(layer, planes, [M, Mn], (160, 240))
    assert out[150, 105, 0] > 0.8
    assert 0.1 < out[150, 62, 0] < 0.6


def test_depth_planes_are_nested():
    layer, mask = figure_scene()
    depth = np.tile(np.linspace(0, 1, 240, dtype=np.float32)[:, None], (1, 160))
    planes = parallax.build_planes(layer, mask, depth)
    a1, a2 = planes["alphas"][0][..., 0], planes["alphas"][1][..., 0]
    assert len(planes["fills"]) == 2
    assert (a1 + 1e-5 >= a2).all()


def test_build_planes_without_maps_is_none():
    layer, _ = figure_scene()
    assert parallax.build_planes(layer) is None
    assert parallax.build_planes(layer, np.zeros(layer.shape[:2], np.float32)) is None


def test_map_cache_key_tracks_raw_hash(tmp_path):
    from PIL import Image

    Image.new("RGB", (8, 8), (10, 20, 30)).save(tmp_path / "03_raw.png")
    assert not parallax.fresh(tmp_path, 3, "mask")
    parallax.save_map(np.ones((8, 8), np.float32), tmp_path / "03_mask.png", "mask")
    (tmp_path / "03_mask.hash").write_text(parallax.map_key(tmp_path / "03_raw.png", "mask"))
    assert parallax.fresh(tmp_path, 3, "mask")
    Image.new("RGB", (8, 8), (11, 20, 30)).save(tmp_path / "03_raw.png")
    assert not parallax.fresh(tmp_path, 3, "mask")


def test_depth_map_roundtrip_16bit(tmp_path):
    d = np.tile(np.linspace(0, 1, 64, dtype=np.float32), (32, 1))
    parallax.save_map(d, tmp_path / "00_depth.png", "depth")
    back = parallax.read_map(tmp_path / "00_depth.png", (64, 32))
    assert np.abs(back - d).max() < 1e-3


def test_ensure_maps_skips_when_no_scene_asks(tmp_path):
    script = {"engine_version": 2, "depth": "off", "scenes": [{"narration": "a"}, {"narration": "b", "kind": "verse", "depth": "mask"}]}
    assert parallax.ensure_maps(script, tmp_path, studio.scene_still) == []


def test_heard_json_written(tmp_path):
    wav = tmp_path / "00.wav"
    studio.write_wav(wav, np.zeros(2400, np.float32))
    rec = studio.write_heard(wav, "hello there", "small", "en")
    on_disk = json.loads((tmp_path / "00.heard.json").read_text())
    assert on_disk == rec
    assert on_disk["wav_sha256"] == studio.file_sha256(wav)
    assert on_disk["text"] == "hello there"


def test_scene_planes_off_for_v1_fields():
    sc = {"narration": "x"}
    assert chalk.scene_planes({"scenes": [sc]}, sc, 0, np.zeros((4, 4, 3), np.float32), None, None) is None
