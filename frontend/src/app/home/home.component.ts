import { Component } from '@angular/core';
import { RouterModule } from '@angular/router';
import { CommonModule } from '@angular/common';

@Component({
  selector: 'app-home',
  standalone: true,
  imports: [CommonModule, RouterModule],
  templateUrl: './home.component.html',
  styleUrls: ['./home.component.css']
})
export class HomeComponent {
  slides = [
    { title: 'Assistant Juridique du Maroc', subtitle: 'Des réponses fiables basées sur la législation marocaine', image: 'assets/hero-morocco.jpeg' },
    { title: 'Vos droits, clarifiés', subtitle: 'Des réponses rapides et fiables', image: 'assets/hero-2.jpg' },
    { title: 'Conforme à la loi', subtitle: 'Références juridiques à l’appui', image: 'assets/hero-3.jpeg' },
  ];

  currentSlide = 0;
  private autoTimer: any;

  ngOnInit() {
    this.startAutoRotate();
  }

  ngOnDestroy() {
    this.stopAutoRotate();
  }

  nextSlide() {
    this.currentSlide = (this.currentSlide + 1) % this.slides.length;
  }

  prevSlide() {
    this.currentSlide = (this.currentSlide - 1 + this.slides.length) % this.slides.length;
  }

  goToSlide(idx: number) {
    this.currentSlide = idx;
  }

  startAutoRotate() {
    this.stopAutoRotate();
    this.autoTimer = setInterval(() => this.nextSlide(), 6000);
  }

  stopAutoRotate() {
    if (this.autoTimer) {
      clearInterval(this.autoTimer);
      this.autoTimer = null;
    }
  }
}
