import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { HistoriqueComponent } from '../historique/historique.component';
import { ChatServiceService } from '../../services/chat-service.service';

@Component({
  selector: 'app-chat',
  standalone: true,
  imports: [CommonModule, FormsModule, HistoriqueComponent],
  templateUrl: './chat.component.html',
  styleUrls: ['./chat.component.css']
})
export class ChatComponent {
  question: string = '';
  messages: { type: 'user' | 'bot', text: string, timestamp: Date }[] = [];
  isLoading: boolean = false;
  isSidebarOpen: boolean = true;
  isDark: boolean = true;

  constructor(private chatService: ChatServiceService) {}

  async sendQuestion() {
    if (!this.question.trim() || this.isLoading) return;

    const userQuestion = this.question.trim();

    // Ajouter message utilisateur
    this.messages.push({
      type: 'user',
      text: userQuestion,
      timestamp: new Date()
    });

    this.question = '';
    this.isLoading = true;

    try {
      // Appel backend
      const response = await this.chatService.askJuridique(userQuestion);

      // Ajouter réponse bot
      this.messages.push({
        type: 'bot',
        text: response.answer,
        timestamp: new Date()
      });
    } catch (error) {
      this.messages.push({
        type: 'bot',
        text: 'Désolé, une erreur est survenue. Veuillez réessayer.',
        timestamp: new Date()
      });
    } finally {
      this.isLoading = false;
      this.scrollToBottom();
    }
  }

  ngOnInit() {
    const saved = localStorage.getItem('chatTheme');
    this.isDark = saved ? saved === 'dark' : true;
  }

  toggleTheme() {
    this.isDark = !this.isDark;
    localStorage.setItem('chatTheme', this.isDark ? 'dark' : 'light');
  }

  toggleSidebar() {
    this.isSidebarOpen = !this.isSidebarOpen;
  }

  private scrollToBottom() {
    setTimeout(() => {
      const messagesContainer = document.querySelector('.messages-container');
      if (messagesContainer) {
        messagesContainer.scrollTop = messagesContainer.scrollHeight;
      }
    }, 100);
  }

  onKeyPress(event: KeyboardEvent) {
    if (event.key === 'Enter' && !event.shiftKey) {
      event.preventDefault();
      this.sendQuestion();
    }
  }
}
