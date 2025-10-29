import { Component, ViewChild } from '@angular/core';
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
  conversationId: string | null = null;
  isLoading: boolean = false;
  isSidebarOpen: boolean = true;
  isDark: boolean = true;
  @ViewChild('hist') historiqueComp?: HistoriqueComponent;

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
      // Créer une conversation si nécessaire
      // Appel backend : le backend gère la création de conversation et la persistance des messages.
      const response = await this.chatService.askWithConversation(userQuestion, this.conversationId || undefined);

      // Mettre à jour l'ID de conversation renvoyé par le backend (créé si nécessaire)
      if (response && response.conversation_id) {
        this.conversationId = response.conversation_id;
      }

      // Ajouter réponse bot localement
      this.messages.push({
        type: 'bot',
        text: response.answer,
        timestamp: new Date()
      });

      // rafraîchir l'historique pour afficher la conversation/dernier message
      try { await this.historiqueComp?.loadHistory(); } catch {}
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

  async onConversationSelected(convId: string | null) {
    if (!convId) {
      // Nouvelle conversation
      this.conversationId = null;
      this.messages = [];
      return;
    }

    this.conversationId = convId;
    try {
      const conv = await this.chatService.getConversation(convId);
      if (conv && conv.messages) {
        this.messages = conv.messages.map((m: any) => ({
          type: m.role === 'user' ? 'user' : 'bot',
          text: m.text,
          timestamp: new Date(m.timestamp)
        }));
      }
      this.scrollToBottom();
    } catch (e) {
      console.warn('Impossible de charger la conversation', e);
    }
  }
}
