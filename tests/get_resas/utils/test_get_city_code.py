from get_resas.utils.get_city_code import get_city_code


def test_get_city_code():
    result = get_city_code()

    # 配列の長さをチェック
    assert len(result) == 1922, "レコード数が市町村数と一致しません"

    # 最初の5行の内容をチェック
    expected_first_5 = [
        ("1", "01100"),  # 北海道札幌市
        ("1", "01101"),  # 北海道函館市
        ("1", "01102"),  # 北海道小樽市
        ("1", "01103"),  # 北海道旭川市
        ("1", "01104"),  # 北海道室蘭市
    ]
    assert result[:5] == expected_first_5, "最初の5行の内容が期待と異なります"
