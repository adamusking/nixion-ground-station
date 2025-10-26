#!/bin/bash
export $(grep -v '^#' .env | xargs)
telegraf --config telegraf.conf
