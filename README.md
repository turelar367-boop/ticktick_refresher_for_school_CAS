# ticktick_refresher_for_school_CAS
Literally,I write a script base on ticktick openAPI and python to realize function of refreshing in school as a indivdual CAS project.
main.py is the entry point of the program. You can deploy it on a server and set up a cron job (scheduled task) for automation. Note: Please pay attention to the timezone difference between your server and your local time.
Configuration: Initialize config and clean_list files by following the templates provided in the application folder.
task_setting is used to define which tasks should execute specific operations.
Authentication:
token_access is a semi-automated script designed to help you obtain your access token.

字面意思，学校CAS项目，基于ticktick openAPI和python 实现ticktick 任务刷新功能。
main.py 是主程序，找个服务器设置定时运行就行了，注意服务器和你所在地的时区问题。config,clean_list 这些文件先创一个application照着填就行了。task_setting 是用来确定哪些任务需要执行哪些操作的。token_access是一个半自动获得access token 的脚本。
