from get_resas.utils.get_ltc_service_category import get_ltc_service_category


def test_get_ltc_service_category():
    result = get_ltc_service_category()

    # 長さチェック
    assert len(result) == 29, "長さが29ではない"
    # 最初の要素の確認
    expected_first_3 = [
        ("0", "000"),
        ("1", "100"),
        ("1", "101"),
    ]
    assert result[:3] == expected_first_3, "最初の3つが一致しない"
