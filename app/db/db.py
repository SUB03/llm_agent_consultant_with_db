from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime, ForeignKey, Boolean, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from datetime import datetime
import uuid

Base = declarative_base()


class Visitor(Base):
    """Таблица анонимных посетителей"""
    __tablename__ = 'visitors'
    
    id = Column(Integer, primary_key=True)
    visitor_id = Column(String(100), unique=True, nullable=False)
    ip_address = Column(String(50))
    user_agent = Column(String(500))
    device_type = Column(String(50))
    browser = Column(String(100))
    first_visit = Column(DateTime, default=datetime.utcnow)
    last_visit = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    sessions = relationship("Session", back_populates="visitor", cascade="all, delete-orphan")


class User(Base):
    """Таблица зарегистрированных пользователей"""
    __tablename__ = 'users'
    
    id = Column(Integer, primary_key=True)
    username = Column(String(100), unique=True, nullable=False)
    email = Column(String(255), unique=True)
    phone = Column(String(50))
    created_at = Column(DateTime, default=datetime.utcnow)
    
    sessions = relationship("Session", back_populates="user", cascade="all, delete-orphan")


class Session(Base):
    """Таблица сессий разговоров"""
    __tablename__ = 'sessions'
    
    id = Column(Integer, primary_key=True)
    visitor_id = Column(Integer, ForeignKey('visitors.id'))
    user_id = Column(Integer, ForeignKey('users.id'))
    session_uuid = Column(String(100), unique=True, default=lambda: str(uuid.uuid4()))
    title = Column(String(255))
    page_url = Column(String(500))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    ended_at = Column(DateTime)
    is_active = Column(Boolean, default=True)
    satisfaction_rating = Column(Integer)
    
    visitor = relationship("Visitor", back_populates="sessions")
    user = relationship("User", back_populates="sessions")
    messages = relationship("Message", back_populates="session", cascade="all, delete-orphan")


class Message(Base):
    """Таблица сообщений"""
    __tablename__ = 'messages'
    
    id = Column(Integer, primary_key=True)
    session_id = Column(Integer, ForeignKey('sessions.id'), nullable=False)
    role = Column(String(50), nullable=False)
    content = Column(Text, nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow)
    tokens_used = Column(Integer)
    
    session = relationship("Session", back_populates="messages")


class KnowledgeBase(Base):
    """База знаний (FAQ)"""
    __tablename__ = 'knowledge_base'
    
    id = Column(Integer, primary_key=True)
    question = Column(Text, nullable=False)
    answer = Column(Text, nullable=False)
    category = Column(String(100))
    keywords = Column(Text)
    priority = Column(Integer, default=0)
    is_active = Column(Boolean, default=True)
    views_count = Column(Integer, default=0)
    helpful_count = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class ChatWidget(Base):
    """Настройки виджета чата"""
    __tablename__ = 'chat_widget'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(100), unique=True, nullable=False)
    welcome_message = Column(Text, default="Здравствуйте! Чем могу помочь?")
    placeholder_text = Column(String(255), default="Введите ваш вопрос...")
    bot_name = Column(String(100), default="Помощник")
    bot_avatar_url = Column(String(500))
    primary_color = Column(String(20), default="#007bff")
    position = Column(String(20), default="bottom-right")
    auto_open_delay = Column(Integer)
    offline_message = Column(Text)
    is_active = Column(Boolean, default=True)
    business_hours = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class Context(Base):
    """Контекст и настройки агента"""
    __tablename__ = 'context'
    
    id = Column(Integer, primary_key=True)
    key = Column(String(255), unique=True, nullable=False)
    value = Column(Text)
    category = Column(String(100))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class Database:
    """Класс для работы с базой данных"""
    
    def __init__(self, db_url='postgresql://user:password@localhost:5432/web_assistant'):
        self.engine = create_engine(db_url, echo=False)
        self.Session = sessionmaker(bind=self.engine)
        
    def create_tables(self):
        """Создать все таблицы"""
        Base.metadata.create_all(self.engine)
        
    def drop_tables(self):
        """Удалить все таблицы"""
        Base.metadata.drop_all(self.engine)
        
    def get_session(self):
        """Получить сессию БД"""
        return self.Session()
    
    def create_or_get_visitor(self, visitor_id=None, ip_address=None, user_agent=None, device_type=None, browser=None):
        """Создать или получить посетителя"""
        session = self.get_session()
        try:
            if visitor_id:
                visitor = session.query(Visitor).filter(Visitor.visitor_id == visitor_id).first()
                if visitor:
                    visitor.last_visit = datetime.utcnow()
                    session.commit()
                    return visitor.id
            
            visitor_uuid = visitor_id or str(uuid.uuid4())
            visitor = Visitor(
                visitor_id=visitor_uuid,
                ip_address=ip_address,
                user_agent=user_agent,
                device_type=device_type,
                browser=browser
            )
            session.add(visitor)
            session.commit()
            return visitor.id
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()
    
    def create_user(self, username, email=None, phone=None):
        """Создать пользователя"""
        session = self.get_session()
        try:
            user = User(username=username, email=email, phone=phone)
            session.add(user)
            session.commit()
            return user.id
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()
    
    def get_user(self, user_id):
        """Получить пользователя"""
        session = self.get_session()
        try:
            return session.query(User).filter(User.id == user_id).first()
        finally:
            session.close()
    
    def create_session(self, visitor_id=None, user_id=None, title=None, page_url=None):
        """Создать сессию"""
        session = self.get_session()
        try:
            chat_session = Session(
                visitor_id=visitor_id,
                user_id=user_id,
                title=title,
                page_url=page_url
            )
            session.add(chat_session)
            session.commit()
            return chat_session.id, chat_session.session_uuid
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()
    
    def end_session(self, session_id, satisfaction_rating=None):
        """Завершить сессию"""
        session = self.get_session()
        try:
            chat_session = session.query(Session).filter(Session.id == session_id).first()
            if chat_session:
                chat_session.is_active = False
                chat_session.ended_at = datetime.utcnow()
                if satisfaction_rating:
                    chat_session.satisfaction_rating = satisfaction_rating
                session.commit()
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()
    
    def get_session_messages(self, session_id):
        """Получить сообщения сессии"""
        session = self.get_session()
        try:
            messages = session.query(Message).filter(
                Message.session_id == session_id
            ).order_by(Message.timestamp).all()
            return messages
        finally:
            session.close()
    
    def add_message(self, session_id, role, content, tokens_used=None):
        """Добавить сообщение"""
        session = self.get_session()
        try:
            message = Message(
                session_id=session_id,
                role=role,
                content=content,
                tokens_used=tokens_used
            )
            session.add(message)
            session.commit()
            return message.id
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()
    
    def set_context(self, key, value, category=None):
        """Сохранить контекст"""
        session = self.get_session()
        try:
            context = session.query(Context).filter(Context.key == key).first()
            if context:
                context.value = value
                context.category = category
                context.updated_at = datetime.utcnow()
            else:
                context = Context(key=key, value=value, category=category)
                session.add(context)
            session.commit()
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()
    
    def get_context(self, key):
        """Получить контекст"""
        session = self.get_session()
        try:
            context = session.query(Context).filter(Context.key == key).first()
            return context.value if context else None
        finally:
            session.close()
    
    def add_knowledge(self, question, answer, category=None, keywords=None):
        """Добавить в базу знаний"""
        session = self.get_session()
        try:
            kb = KnowledgeBase(
                question=question,
                answer=answer,
                category=category,
                keywords=keywords
            )
            session.add(kb)
            session.commit()
            return kb.id
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()
    
    def search_knowledge(self, query, category=None, limit=5):
        """Поиск в базе знаний"""
        session = self.get_session()
        try:
            q = session.query(KnowledgeBase).filter(KnowledgeBase.is_active == True)
            if category:
                q = q.filter(KnowledgeBase.category == category)
            q = q.filter(
                (KnowledgeBase.question.ilike(f'%{query}%')) |
                (KnowledgeBase.keywords.ilike(f'%{query}%'))
            )
            return q.order_by(KnowledgeBase.priority.desc()).limit(limit).all()
        finally:
            session.close()
    
    def get_widget_settings(self, name='default'):
        """Получить настройки виджета"""
        session = self.get_session()
        try:
            return session.query(ChatWidget).filter(ChatWidget.name == name).first()
        finally:
            session.close()
    
    def update_widget_settings(self, name, **kwargs):
        """Обновить настройки виджета"""
        session = self.get_session()
        try:
            widget = session.query(ChatWidget).filter(ChatWidget.name == name).first()
            if not widget:
                widget = ChatWidget(name=name)
                session.add(widget)
            
            for key, value in kwargs.items():
                if hasattr(widget, key):
                    setattr(widget, key, value)
            
            session.commit()
            return widget.id
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()
