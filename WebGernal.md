# Django+Vue.js构建通用数据分析可视化平台

> 半年前为实验室智能决策项目构建的通用数据分析可视化平台，临近毕业，项目交接，因而整理了Django和Vue之间结合的流程及关键步骤，以供参考。本文的目标是让每一个有一定基础的开发者都能完整的复现整个项目。

django功能强大，易于上手，但前端的模版系统使前后端严重耦合，因而想仅使用django的后端即model和路由，作为服务提供api接口，而在前端使用vue.js。

之后会从两个案例说明如何将Django和vue.js二者结合，案例一是blog项目，案例二是通用管理平台。

## 两个案例

首先我们创建一个全新的Django工程“DjangoVuejs”来包含这两个案例。

首先建立一个虚拟python环境，在安装完依赖包之后，可以到导出依赖到文件：

```shell
pip freeze > requirements.txt
```



参考[文档](https://docs.djangoproject.com/en/2.0/intro/tutorial01/)创建新的Django工程。

```shell
# 基本指令
django-admin startproject mysite
python manage.py startapp polls
python manage.py runserver
python manage.py makemigrations polls
python manage.py sqlmigrate polls 0001  # create sql
python manage.py migrate  # create table in database
python manage.py shell
python manage.py createsuperuser  
```

- 数据库修改为mysql

  安装pymysql模块，在项目目录下的__init__.py文件中添加以下内容：

  ```python
  import pymysql
  pymysql.install_as_MySQLdb() 
  ```

  在setting文件中修改数据库配置：

  ```python
  DATABASES = {
      'default': {
          'ENGINE': 'django.db.backends.mysql',
          'NAME': 'DjangoVuejs',
          'USER': 'root',
          'PASSWORD': '123456',
          'HOST': 'localhost',
          'PORT': '3306',
      }
  }
  ```

按照官网的示例建立polls这个项目后，对django的工作流应当没有问题了，下面开启Django和Vue.js双剑合壁。

### Blog项目

本项目直接选取两个已经构建后的blog的django后端和Vue.js前端(是我浏览博客时发现的自己喜欢风格的blog，直接保存网页用vue重写)，重点给出二者如何结合以及结合过程中可能出现的问题及解决方法，下面的描述会简化实现细节，重点说明二者的结合，项目源码(link)。



在开始之前，以Blog前端界面为例简要回顾一个Vue.js项目的流程。

#### Vue.js构建Blog前端

>前提：安装[node.js](https://nodejs.org/en/download/),安装vue和vue-cli(帮助构建vue项目的框架)。

1. 进入项目主目录DjangoVuejs ，创建前端工程blogfront

   ```shell
   >>> vue-init webpack blogfront 
   >>> cd blogfront
   >>> npm install
   # 可以通过如下操作解决npm速度慢的问题
   >>> npm install --registry=https://registry.npm.taobao.org 
   >>> npm run dev
   >>> npm run build
   # npm install出现后可以试着执行下面的质量解决问题
   >>> npm cache clean --force
   ```

   build之后会在dist文件夹下有打包好后的代码。

   回过头来查看vue项目的结构，重点需要关注的是src目录，src目录下包含入口文件main.js，入口组件App.vue,组件目录components，路由目录router，后缀为vue的文件是Vue.js框架定义的单文件组件，内容一般分且仅分为三块：前端的渲染模版`template`、渲染逻辑`script`和模版样式`style`.

   - 安装在main.js中引入的组件

     ```
     npm install --save  element-ui vue-awesome vue-awesome/icons vue-multiple-back-top vue-resource vuex vue-filter
     ```
     在项目根目录下的package.json的dependencies会添加用到的依赖项。

   - 前端路由

     Vue.js构建的是单页应用，映射规则由前端路由定义。

2. 在Django中整合静态文件

   在Django的setting文件中添加以下配置：

   - Setting-Static

     ```python
     STATICFILES_DIRS = [
         os.path.join(BASE_DIR, "blogfront/dist/static"),
     ]
     ```

   - Setting-Templates

     ```
     TEMPLATES = [{
     	'BACKEND': 'django.template.backends.django.DjangoTemplates',
      	'DIRS':	['your_django_root/blogfront/dist'],
         'APP_DIRS': True,
         'OPTIONS':
         	{'context_processors': [
                     'django.template.context_processors.debug',
                     'django.template.context_processors.request',
                     'django.contrib.auth.context_processors.auth',    								'django.contrib.messages.context_processors.messages',
                 ],
             },
         },
     ]
     ```

   - 修改Django主目录urls：

     添加一条对主页的路由：

     ```python
     urlpatterns = [
         path(r'', TemplateView.as_view(template_name='index.html')),
         path('polls/', include('polls.urls')),
         path('admin/', admin.site.urls),
     ]
     ```

3. 可能存在的异常问题处理

   - 跨域请求问题

   ```
   No 'Access-Control-Allow-Origin' header is present on the requested resource
   ```

      这时候我们须要在Django层注入header，用Django的第三方包`django-cors-headers`来解决跨域问题：`pip install django-cors-headers`

      settings.py 有两处修改：

   ```
   MIDDLEWARE = [
       'django.middleware.security.SecurityMiddleware',
       'django.contrib.sessions.middleware.SessionMiddleware',
       'corsheaders.middleware.CorsMiddleware', # this line 添加此行
       'django.middleware.common.CommonMiddleware',
       'django.middleware.csrf.CsrfViewMiddleware',
       'django.contrib.auth.middleware.AuthenticationMiddleware',
       'django.contrib.messages.middleware.MessageMiddleware',
       'django.middleware.clickjacking.XFrameOptionsMiddleware',
   ]
   CORS_ORIGIN_ALLOW_ALL = True # this line 添加此行
   ```
### 管理网站

网站的源码来源于[vue-element-admin](http://panjiachen.github.io/vue-element-admin)及[vueAdmin-template](https://github.com/PanJiaChen/vueAdmin-template)，是一个后台集成解决方案，它基于 [vue](https://github.com/vuejs/vue) 和 [element](https://github.com/ElemeFE/element)。它使用了最新的前端技术栈，内置了i18国际化解决方案，动态路由，权限验证，提炼了典型的业务模型，提供了丰富的功能组件，它可以帮助你快速搭建企业级中后台产品原型。结合其现有组件结构，使用django提供数据分析的api接口，构建数据分析可视化平台。

### 工程部署

工程部署到nginx，仍能引用静态文件

sudo ln -s /your/path/nginx.conf  /etc/nginx/sites-enabled/  

1. 通过工具创建vue工程

   构建Vue.js前端项目

   ```sh
   npm install -g vue-cli
   vue-init webpack appfront  //安装中把vue-router选上，我们须要它来做前端路由
   npm install //安装vue所须要的node依赖
   ```

vue的router并不是地址栏的地址，而是页面间跳转，解析时会在路径前添加“#”

> 安装依赖：cnpm install sass-loader --save-dev；cnpm install --save-dev node-sass
>
> cnpm install css-loader --save-dev；cnpm install --save-dev node-css

## Vue相关

- vue-cli目录结构

  ```
  ├── README.md  // 项目说明
  ├── build  // 项目构建(webpack)相关代码
  │   ├── build.js  // 生产环境构建代码
  │   ├── check-versions.js  // 检查node、npm等版本
  │   ├── logo.png
  │   ├── utils.js  // 构建工具相关
  │   ├── vue-loader.conf.js  
  │   ├── webpack.base.conf.js  // webpack基础配置
  │   ├── webpack.dev.conf.js  // webpack开发环境配置
  │   └── webpack.prod.conf.js  // webpack生产环境配置
  ├── config  // 项目开发环境配置
  │   ├── dev.env.js  // 开发环境变量
  │   ├── index.js  // 项目一些配置变量
  │   ├── prod.env.js  // 生产环境变量
  │   └── test.env.js  // 测试环境变量
  ├── index.html  // 入口页面
  ├── package.json  //项目基本信息
  ├── src  // 源码目录
  │   ├── App.vue  // 页面入口文件
  │   ├── assets  // 资源目录 
  │   ├── components  // vue公共组件
  │   ├── main.js  // 程序入口文件，加载各种公共组件
  │   └── router
  ├── static  // 静态文件，比如一些图片，json数据等
  └── test
      ├── e2e
      └── unit
  ```

- npm源

```shell
npm install --registry=https://registry.npm.taobao.org
```

- 禁用eslint

  在`config/index.js`下修改`useEslint: False`

- vue语法：

事件及事件修饰符

语法糖：

`<comp :foo.sync="bar"></comp>`

`.sync`等价于

`<comp :foo="bar" @update:foo="val => bar = val"></comp>`

子组件向父组件传递值：



文档

https://cn.vuejs.org/v2/guide/conditional.html#v-if

https://router.vuejs.org/zh-cn/essentials/named-routes.html

https://vue-loader.vuejs.org/zh-cn/?q=

https://vuex.vuejs.org/zh-cn/state.html

不要丢失了最初的目标：

https://github.com/PanJiaChen/vue-element-admin

https://panjiachen.github.io/vue-element-admin-site/#/zh-cn/

https://elemefe.github.io/v-charts/#/

http://element-cn.eleme.io/#/zh-CN/guide/nav
