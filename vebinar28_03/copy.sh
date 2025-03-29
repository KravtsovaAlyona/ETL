#!/bin/bash

SOURCE_DIR="/home/mgpu/Downloads/workshop-on-ETL-main/business_case_rocket_25/data/images"  # папка с фото
DEST_DIR="/home/mgpu/Downloads/photo"  # папка для копирования
LOG_FILE="/home/mgpu/Downloads/workshop-on-ETL-main/business_case_rocket_25/logs/copy.log"  # файл с логами

# Проверяем существование папок
if [ ! -d "$SOURCE_DIR" ]; then
    echo "$(date): Ошибка! Исходная папка не найдена: $SOURCE_DIR" | tee -a "$LOG_FILE"
    exit 1
fi

if [ ! -d "$DEST_DIR" ]; then
    echo "$(date): Папка назначения не найдена, создаем: $DEST_DIR" | tee -a "$LOG_FILE"
    mkdir -p "$DEST_DIR"
fi

# Копирование файлов
echo "$(date): Начинаем копирование файлов из $SOURCE_DIR в $DEST_DIR." | tee -a "$LOG_FILE"
cp -r "$SOURCE_DIR"/* "$DEST_DIR"

# Завершающее сообщение
echo "$(date): Процесс копирования завершен." | tee -a "$LOG_FILE"