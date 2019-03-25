import { Component, OnInit, ElementRef, Renderer2 } from '@angular/core';
import { EnrollmentModal } from '@heartsteps/enrollment/enroll';
import { Router } from '@angular/router';

@Component({
  selector: 'page-welcome',
  templateUrl: 'welcome.html',
  entryComponents: [
    EnrollmentModal
  ]
})
export class WelcomePage implements OnInit {

  constructor(
    private el:ElementRef,
    private renderer:Renderer2,
    private router: Router
  ) {}

  goToEnrollPage() {
    this.router.navigate([{outlets: {
      modal: 'enroll'
    }}]);
  }

  ngOnInit() {
    this.renderer.addClass(this.el.nativeElement, 'start-screen')
  }

}
