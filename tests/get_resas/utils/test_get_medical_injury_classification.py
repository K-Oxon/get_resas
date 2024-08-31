from get_resas.utils.get_medical_injury_classification import (
    get_medical_injury_classification,
)


def test_get_medical_injury_classification():
    result = get_medical_injury_classification()

    # 長さチェック
    assert len(result) == 82, "長さが82ではない"
    # 最初の要素の確認
    expected_first_3 = [
        ("00", "000"),
        ("01", "010"),
        ("01", "011"),
    ]
    assert result[:3] == expected_first_3, "最初の3つが一致しない"
