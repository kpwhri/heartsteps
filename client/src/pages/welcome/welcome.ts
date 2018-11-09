import { Component, OnInit, ElementRef, Renderer2 } from '@angular/core';
import { IonicPage, NavController } from 'ionic-angular';
import { EnrollPage } from '@heartsteps/enrollment/enroll';

@Component({
  selector: 'page-welcome',
  templateUrl: 'welcome.html',
  entryComponents: [
    EnrollPage
  ]
})
export class WelcomePage implements OnInit {

  constructor(
    private navCtrl: NavController,
    private el:ElementRef,
    private renderer:Renderer2
  ) {}

  goToEnrollPage() {
    this.navCtrl.push(EnrollPage)
  }

  ngOnInit() {
    this.renderer.addClass(this.el.nativeElement, 'start-screen')
  }

}
