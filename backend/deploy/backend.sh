#!/bin/bash

function unit_test(){
    echo "开始运行后端单元测试..."
    
    if [[ ! -d "./backend/tests_api" ]]; then
        echo "错误：测试目录 ./backend/tests_api 不存在"
        exit 1
    fi
    
    # 运行单元测试
    cd ./backend
    pytest tests_api/ -v
    
    # 检查测试结果
    if [[ $? -ne 0 ]]; then
        echo "错误：单元测试未全部通过，停止部署"
        cd ..
        exit 1
    fi
    
    echo "所有单元测试通过，继续部署..."
    cd ..
}

function backend_to_remote() {
    unit_test
    
    backend_tar="flasky_backend.tar"
    if [[ -e  $backend_tar ]];then
      rm -f $backend_tar
      echo "已删除 $backend_tar"
    fi

    # 构建镜像并保存为tar文件
    if sysctl -n machdep.cpu.brand_string | grep -q "Apple"; then
      # mac芯片为M4，指定平台为 linux/amd64
      docker build --platform linux/amd64 -t nizhenshi/flasky_backend ./backend
    else
      docker build -t nizhenshi/flasky_backend ./backend
    fi
    docker save -o flasky_backend.tar nizhenshi/flasky_backend

    # 传输.env.production
    ENV_FILE=".env.prod"
    LOCAL_ENV_FILE="./backend/$ENV_FILE"
    REMOTE_ENV_DIR="/home/ubuntu/user/loft/"
    scp $LOCAL_ENV_FILE $ROMOTE_USER@$ROMOTE_HOST:$REMOTE_ENV_DIR
    if [[ $? -eq 0 ]];then
      echo "环境变量文件传输成功 $LOCAL_FILE"
    else
      echo "环境变量文件传输失败"
    fi

    # 传输tar文件到远程服务器
    LOCAL_FILE=$backend_tar
    REMOTE_FILE="/home/ubuntu/user/"
    scp $LOCAL_FILE $ROMOTE_USER@$ROMOTE_HOST:$REMOTE_FILE
    if [[ $? -eq 0 ]];then
      echo "传输成功 $LOCAL_FILE"
    else
      echo "传输失败"
    fi
    if [[ -e  $backend_tar ]];then
      rm -f $backend_tar
      echo "已删除 $backend_tar"
    fi

    # 远程运行容器命令
    remote_del_old_container="docker rm -f flasky_backend;docker rmi nizhenshi/flasky_backend;"
    remote_load_new_container="docker load -i flasky_backend.tar;"
    remote_run_new_container="docker run --name flasky_backend --env-file $REMOTE_ENV_DIR$ENV_FILE -v /var/log/loft:/home/flasky/logs -d -p 4289:5000  -p 4290:5001 --network database_n nizhenshi/flasky_backend:latest;"
    remote_cmd_backend="$remote_del_old_container $remote_load_new_container $remote_run_new_container"
    echo "remote_cmd_backend:" $remote_cmd_backend
    ssh $ROMOTE_USER@$ROMOTE_HOST "cd $REMOTE_ENV_DIR;chmod 600 $ENV_FILE;cd $REMOTE_FILE;$remote_cmd_backend"
    if [[ $? -eq 0 ]];then
      echo "执行成功"
    else
      echo "执行失败"
    fi
}

