# ec2批量操作GUI

### 新增docker部署方案
### 新增可以依照檔案後面編號上傳到個別ec2功能

## Docker使用方式:
1. ## 把AWS CLI config,credentials,ec2的金鑰放到config資料夾裡,不知道CLI config的可以看 [AWS Support](https://docs.aws.amazon.com/zh_tw/cli/latest/userguide/cli-configure-profiles.html).
1. ## 使用tool裡面的encrypt(改用encryptfile,decryptfile註解掉,加密完再改回去)把剛剛那三個檔案加密以防金鑰洩漏
1. ## 依照個人狀況修改config.txt
1. ## docker image build -t dockerfile .
1. ## docker run -it  -p 80:5000  -v 預設上傳/下載路徑:/app/ec2download --name ec2 dockerfile

## 一般使用方式:
1. ## 依照個人狀況修改config.txt
1. ## 使用ec2api
