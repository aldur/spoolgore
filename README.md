你好！
很冒昧用这样的方式来和你沟通，如有打扰请忽略我的提交哈。我是光年实验室（gnlab.com）的HR，在招Golang开发工程师，我们是一个技术型团队，技术氛围非常好。全职和兼职都可以，不过最好是全职，工作地点杭州。
我们公司是做流量增长的，Golang负责开发SAAS平台的应用，我们做的很多应用是全新的，工作非常有挑战也很有意思，是国内很多大厂的顾问。
如果有兴趣的话加我微信：13515810775  ，也可以访问 https://gnlab.com/，联系客服转发给HR。
Spoolgore
=========

A simple mail "spool and send" daemon written in Go

Building it
===========

```sh
go build spoolgore.go
```

that's all...

Using it
========


```sh
# send every mail spooled to /var/spool/yourapp via example.com smtp service
spoolgore -smtpaddr example.com:25 /var/spool/yourapp
```

```sh
# send every mail spooled to /var/spool/yourapp via foobar.it smtp service using plain authentication
spoolgore -smtpaddr foobar.it:25 -smtpuser kratos -smtppassword deimos /var/spool/yourapp
```

```sh
# send every mail spooled to /var/spool/yourapp via example.com smtp service, do not try for more than 30 times on smtp error
spoolgore -smtpaddr example.com:25 -attempts 30 /var/spool/yourapp
```

JSON status file
================

During its lifecycle, Spoolgore constantly updates a json file with its internal status. You can simply view that file
to understand what is going on. By default the file is stored as .spoolgore.js in your spool directory, but you can change its path with the -json option.

Options
=======

-smtpaddr

-smtpuser

-smtppassword

-smtpmd5user

-smtpmd5password

-freq

-attempts

-json

Signals
=======

SIGURG -> suddenly re-scan the queue

SIGHUP -> reload the json status file

SIGTSTP -> block queue scan, useful for manually updating the json status

Why ?
=====

Sending e-mails from your app via remote smtp can be a huge problem: if your smtp service is slow, your app will be slow, if your service is blocked your app will be blocked. If you need to send a gazillion email in one round your app could be blocked for ages.

"spool and send" daemons allow you to store the email as a simple file on a directory (the 'spool' directory), while a background daemon will send it as soon as possible, taking care to retry on any error.

Projects like nullmailer (http://untroubled.org/nullmailer/) work well, but they are somewhat limited (in the nullmailer case having multiple instances running on the system requires patching).

Spoolgore tries to address the problem in the easiest possible way.

Why Go ?
========

MTAs (and similar) tend to spawn an additional process for each SMTP transaction. This is good (and holy) for privileges separation, but spoolgore is meant to be run by each user (or single application stack) so we do not need this kind of isolation in SMTP transactions.

Go (thanks to goroutines) allows us to enqueue hundreds of SMTP transactions at the cost of few KB of memory.

Obviously we could have written it in python/gevent or perl/coro::anyevent or whatever non-blocking coroutine/based technology you like, but we choose go as we wanted to give it a try (yes, no other reasons)

TODO
====

implement rate limiter (lot of services limit the number of emails you can enqueue per minute/hour)

Issues
======

windows is not supported, if you want to use Spoolgore on it, just patch the code to not use syscall.SIGURG and syscall.SIGTSTP
