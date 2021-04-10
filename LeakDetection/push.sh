cd ..
docker build -f LeakDetection/Dockerfile -t jonev/leak-detection .
docker push jonev/leak-detection