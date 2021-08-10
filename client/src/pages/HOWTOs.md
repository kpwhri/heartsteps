# HOWTO's 

## How to create an hello world landing page

### Goal

* Create a "hello-world" page with direct access url of "http://localhost:8100/#/hello"

### Requirements

* Any modern web browser

### Start

* If you are logged in, go to settings and log out.

* If you haven't done anything yet, http://localhost:8100/#/hello leads you to the welcome page (http://localhost:8100/#/welcome). Let's change that first.

* If you connect to **/hello**, what happens? The console says like this:

```
core.js:1449 ERROR Error: Uncaught (in promise): Error: Cannot match any routes. URL Segment: 'hello'
Error: Cannot match any routes. URL Segment: 'hello'
```
* Where does it look up "hello"? 

* Go to ***/client/src/app/app.module.ts*** and add ***HelloModule*** in **@NGModule > imports**. Also, add the following in the declarations above.

```
import { HelloModule } from "@pages/hello/hello.module";
```

* Save, and access to the url again. We haven't created the "hello" folder and "hello.module", it will say like this:

```
Runtime Error
Cannot find module "@pages/hello/hello.module"
Stack
Error: Cannot find module "@pages/hello/hello.module"
    at Object.798 (http://localhost:8100/build/main.js:19726:7)
    at __webpack_require__ (http://localhost:8100/build/vendor.js:55:30)
    at Object.793 (http://localhost:8100/build/main.js:19701:70)
    at __webpack_require__ (http://localhost:8100/build/vendor.js:55:30)
    at webpackJsonpCallback (http://localhost:8100/build/vendor.js:26:23)
    at http://localhost:8100/build/main.js:1:1
```

* Let's create them. Create "hello" folder in **/client/src/page**. And reload it again. The same. We create a file named ***hello.module.ts*** in the folder. For now, let's keep it empty.

* Still, it cannot find the "HelloModule". It's because the file should contain the description about the module. So, let's add this in the hello.module.ts file:

```
export class HelloModule {}
```

* The error message is changed.

```
Runtime Error
Unexpected value 'undefined' imported by the module 'AppModule'
Stack
Error: Unexpected value 'undefined' imported by the module 'AppModule'
    at syntaxError (http://localhost:8100/build/vendor.js:133855:34)
    at http://localhost:8100/build/vendor.js:148615:40
    at Array.forEach (<anonymous>)
    at CompileMetadataResolver.getNgModuleMetadata (http://localhost:8100/build/vendor.js:148584:49)
    at JitCompiler._loadModules (http://localhost:8100/build/vendor.js:167782:87)
    at JitCompiler._compileModuleAndComponents (http://localhost:8100/build/vendor.js:167743:36)
    at JitCompiler.compileModuleAsync (http://localhost:8100/build/vendor.js:167637:37)
    at CompilerImpl.compileModuleAsync (http://localhost:8100/build/vendor.js:132676:49)
    at PlatformRef.bootstrapModule (http://localhost:8100/build/vendor.js:5903:25)
    at Object.793 (http://localhost:8100/build/main.js:19743:109)
```

* It means that importing HelloModule was possible, but there was nothing (undefined) in it. So, AppModule cannot import "undefined" thing. So, let's define something in HelloModule. Put these codes ***above*** the line starting with "export"

```
@NgModule({
  declarations: [
  ],
  imports: [
  ],
  exports: [
  ],
  providers: [
  ]
})
```

* The new error message is like this. 
```
Runtime Error
NgModule is not defined
Stack
ReferenceError: NgModule is not defined
    at http://localhost:8100/build/main.js:10243:5
    at Object.1592 (http://localhost:8100/build/main.js:10252:2)
    at __webpack_require__ (http://localhost:8100/build/vendor.js:55:30)
    at Object.798 (http://localhost:8100/build/main.js:19779:85)
    at __webpack_require__ (http://localhost:8100/build/vendor.js:55:30)
    at Object.793 (http://localhost:8100/build/main.js:19754:70)
    at __webpack_require__ (http://localhost:8100/build/vendor.js:55:30)
    at webpackJsonpCallback (http://localhost:8100/build/vendor.js:26:23)
    at http://localhost:8100/build/main.js:1:1
```

* It means we used a specific key word (NgModule) and it is not primitive keyword and not defined anywhere. Yes, it is a core component of Angular framework. We should declare where we (the compiler) can find about NgModule. Let's add one line on the top of the file.

```
import { NgModule } from '@angular/core';
```

* Tada~ Now it's not making any errors again, but still we're redirected to the "welcome" page. Why? We had included the "HelloModule" but it is practically empty. So, the AppModule looked inside but there was nothing ***HOLDS US BACK*** in the hello module. What we should do is making something holds us back somewhere in HelloModule. How could we do that? The only thing that makes us special is the URL we're trying to reach. The request for "http://localhost:8100" and us ("http://localhost:8100/#/hello) are different only in the matter of URL. So, we have to give the HelloModule some hint about the url we're trying to reach. Put this code between  "import" and @NgModule.

```
import { Routes } from '@angular/router';
import { HelloPage } from './hello';

const routes: Routes = [{
  path: 'hello',
  component: HelloPage
}];
```

* ***routes*** will have one hint (since it is an array, it can contain multiple hints. But for now, we only give it a single hint.): "hello". This means we can be identified with that path, and somebody (Route class) will "route" us to another class "HelloPage". ***Route*** class is responsible for 
    - identifying requests with path string
    - reroute them to specific class so that the destination class can handle us

* Route class is not a primitive keyword, so we have to import it from Angular framework. We also need to import HelloPage class which will handle us from somewhere else.('./hello.ts'. When you import, '.ts' is omitted.) But It is not defined yet.

* So, we have to create "hello.ts" which contains about HelloPage class. Let's do that. This is a source code for HelloPage class.

```
import { Router } from '@angular/router';

export class HelloPage {
  constructor(
    private router: Router
  ) {}
}
```

* Even after you create that handler (hello.ts) and the routing hint (route), the URL still redirects you to welcome page. What is wrong with it? --- We haven't given the ***route*** hint to HelloModule. So, the AppModule looks up in HelloModule, but it doesn't have any effective hint for selective routing. We will create that now. Let's change ***imports*** in the @NgModule definition like this:

```
  imports: [
    RouterModule.forChild(routes)
  ],
```

* and to import RouterModule, let's add the following line in hello.module.ts at the top.

```
import { RouterModule } from '@angular/router';
```

* Then, something is changed. The url doesn't bring us to welcome page. It brings us to an empty page. (Yay!) Let's add something in the page.

* Ah, there's another error message in the console. Something like this:

```
core.js:1449 ERROR Error: Uncaught (in promise): Error: No component factory found for HelloPage. Did you add it to @NgModule.entryComponents?
Error: No component factory found for HelloPage. Did you add it to @NgModule.entryComponents?
```

* It says we need component factory in HelloPage. Let's add it then. Add this to hello.ts between **import** and **export**.

```
import { Component } from '@angular/core';

@Component({
  selector: 'page-hello',
  templateUrl: 'hello.html',
  entryComponents: [
  ]
})
```

* This paragraph means the following:
    - this page will be fetched by 'page-hello' in the source code
    - we will use the HTML template named 'hello.html'
    - we don't have anything yet as an entryComponents

* Then, let's add **hello.html** in the same directory.

```
<p>Hello HeartSteps</p>
```

* I thought we're near the end. But it gives us another error message like this:

```
Runtime Error
Component HelloPage is not part of any NgModule or the module has not been imported into your module.
Stack
Error: Component HelloPage is not part of any NgModule or the module has not been imported into your module.
```

* Let's do whatever it says. I guess "any NgModule" would be NgModule block in hello.module.ts file. So, let's go there and add it in the declaration part.

```
@NgModule({
  declarations: [
    HelloPage
  ],
...
```

* Hurray! It shows black small letters: "Hello HeartSteps". The following is the resulting codes:

### client/src/app/app.module
```
...
import { HelloModule } from "@pages/hello/hello.module";
...

@NgModule({
    ...
    imports: [
        ...
        HelloModule,
        ...
    ],
    ...
```

### client/src/pages/hello/hello.html
```
<p>Hello HeartSteps</p>
```

### client/src/pages/hello/hello.module.ts
```
import { NgModule } from '@angular/core';
import { Routes } from '@angular/router';
import { RouterModule } from '@angular/router';
import { HelloPage } from './hello';

const routes: Routes = [{
  path: 'hello',
  component: HelloPage
}];

@NgModule({
  declarations: [
    HelloPage
  ],
  imports: [
    RouterModule.forChild(routes)
  ],
  exports: [
  ],
  providers: [
  ]
})
export class HelloModule { }
```

### client/src/pages/hello/hello.ts
```
import { Router } from '@angular/router';

import { Component } from '@angular/core';

@Component({
  selector: 'page-hello',
  templateUrl: 'hello.html',
  entryComponents: [
  ]
})

export class HelloPage {
  constructor(
    private router: Router
  ) {}
}
```