import { Component, OnInit, ElementRef, Renderer2 } from '@angular/core';
import { EnrollmentModal } from '@heartsteps/enrollment/enroll';
import { Router } from '@angular/router';

declare var process: {
  env: {
      BUILD_VERSION: string,
      BUILD_DATE: string
  }
}

@Component({
  selector: 'page-welcome',
  templateUrl: 'welcome.html',
  entryComponents: [
    EnrollmentModal
  ]
})
export class WelcomePage implements OnInit {

  public buildVersion: string = process.env.BUILD_VERSION;
  public buildDate: string = process.env.BUILD_DATE;

  constructor(
    private el:ElementRef,
    private renderer:Renderer2,
    private router: Router
  ) {}

  goToEnrollPage() {
    this.router.navigate(['enroll']);
  }

  ngOnInit() {
    this.renderer.addClass(this.el.nativeElement, 'start-screen')
  }

}
