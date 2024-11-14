from ai_screenshot_namer.main import _calc_max_image_size


def test_calc_max_image_size():
    assert _calc_max_image_size((2000, 768)) == (2000, 768)

    assert _calc_max_image_size((512, 1024)) == (512, 1024)

    # short side should be <= 468
    assert _calc_max_image_size((1024, 800)) == (983, 768)

    # also long side as height not width
    assert _calc_max_image_size((800, 1024)) == (768, 983)
