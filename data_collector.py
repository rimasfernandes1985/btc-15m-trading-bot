name: BTC Data Collector
on:
  schedule:
    - cron: '*/15 * * * *'
  workflow_dispatch:
jobs:
  collect:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.10'
      - name: Install dependencies
        run: pip install ccxt pandas
      - name: Run data collector
        run: python data_collector.py
      - name: Commit and push
        run: |
          git config --global user.email "you@example.com"
          git config --global user.name "GitHub Actions"
          git add btc_data.csv
          git commit -m "Update BTC data"
          git push
