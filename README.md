# get_resas

```bash
rye sync
dotenvx run -- rye run get_resas
```

## 定義済一覧

WIP

## 設定など

- rye
- dotenvx

```bash
cp .env_sample .env
```

`.env`に取得したRESAS API KEYを記載

`.dlt/config.toml`に宛先のdataset_nameを記載

## 取得内容の追加

1. `src/get_resas/congig/`配下に`.py`ファイルを追加する
2. 他のファイルを参考にRequestModelを定義する
   1. レスポンスのモデルは必須ではない
3. `src/get_resas/pipelines/`配下に`.py`ファイルを追加しAPIからデータを取得するジョブを定義する
4. `dotenvx run -- rye run python src/get_resas/pipeline/[YOUR_NEW_PIPELINE].py`などで実行を確認
5. 必要に応じてmain.pyに追記する

## TODO

- [ ] API Client と transformerを使ったリファクタ
  - https://dlthub.com/docs/general-usage/resource#process-resources-with-dlttransformer
  - https://dlthub.com/docs/general-usage/http/rest-client
- [ ] BigQuery Adapterでdescription追加
  - https://dlthub.com/docs/api_reference/destinations/impl/bigquery/bigquery_adapter
