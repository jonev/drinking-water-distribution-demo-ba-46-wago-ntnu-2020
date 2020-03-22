cd ..
docker buildx build -f LeakDetection/Dockerfile -t jonev/leak-detection --push .