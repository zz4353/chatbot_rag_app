#### Dùng python 3.12

1. Cài đặt Docker:
    Tải và cài đặt: https://www.docker.com/products/docker-desktop/


2. Cài đặt và chạy elasticsearch.
Chạy đoạn này:
    docker run -p 127.0.0.1:9200:9200 -d --name elasticsearch -e "discovery.type=single-node" -e "xpack.security.enabled=false" -e "xpack.license.self_generated.type=trial" -v "elasticsearch-data:/usr/share/elasticsearch/data" docker.elastic.co/elasticsearch/elasticsearch:8.15.0

    Nguồn: https://www.elastic.co/search-labs/tutorials/install-elasticsearch/docker





3. Cài đặt Nodejs, yarn
    Link: https://nodejs.org/en

    npm install -g yarn
    yarn install




Run
    Terminal 1:
        flask create-index
        flask run --port=3001
    Terminal 2:
        cd frontend
        yarn start