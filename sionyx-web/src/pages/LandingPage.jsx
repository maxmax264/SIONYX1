/**
 * SIONYX Landing Page v3.0
 * Premium animated landing experience with immersive motion design
 * Enhanced with refined visuals, better typography, and polished animations
 */

import { useState, useCallback, useEffect, useRef, memo } from 'react';
import { motion, useScroll, useTransform, useSpring } from 'framer-motion'; // eslint-disable-line no-unused-vars
import { Typography, Space, Row, Col, Tag, Divider } from 'antd';
import {
  SettingOutlined,
  TeamOutlined,
  CrownOutlined,
  PhoneOutlined,
  MailOutlined,
  ThunderboltOutlined,
  SafetyCertificateOutlined,
  ClockCircleOutlined,
  DashboardOutlined,
  PrinterOutlined,
  CloudOutlined,
  MobileOutlined,
  ApiOutlined,
  CheckCircleOutlined,
} from '@ant-design/icons';
import { useNavigate } from 'react-router-dom';
import gsap from 'gsap';
import { ScrollTrigger } from 'gsap/ScrollTrigger';

import {
  AnimatedBackground,
  AnimatedButton,
  AnimatedCard,
  GlowingText,
  GradientText,
} from '../components/animated';

gsap.registerPlugin(ScrollTrigger);

const { Title, Paragraph, Text } = Typography;

// Premium color palette
const colors = {
  primary: '#667eea',
  primaryLight: '#8b9df0',
  secondary: '#764ba2',
  accent: '#ec4899',
  success: '#10b981',
  warning: '#f59e0b',
  info: '#3b82f6',
  cyan: '#06b6d4',
  orange: '#f97316',
};

// ============================================
// Hero Section Component - Premium v2.0
// ============================================
const HeroSection = memo(({ onAdminLogin }) => {
  const heroRef = useRef(null);
  const subtitleRef = useRef(null);

  // Parallax effect on scroll — spring-smoothed for buttery feel
  const { scrollY } = useScroll();
  const rawY = useTransform(scrollY, [0, 500], [0, 100]);
  const rawOpacity = useTransform(scrollY, [0, 400], [1, 0]);
  const rawScale = useTransform(scrollY, [0, 400], [1, 0.95]);
  const springConfig = { stiffness: 100, damping: 30, mass: 0.5 };
  const y = useSpring(rawY, springConfig);
  const opacity = useSpring(rawOpacity, springConfig);
  const scale = useSpring(rawScale, springConfig);

  // Subtitle GSAP animation
  useEffect(() => {
    const ctx = gsap.context(() => {
      if (subtitleRef.current) {
        gsap.fromTo(
          subtitleRef.current,
          { opacity: 0, y: 20 },
          { opacity: 1, y: 0, duration: 1, delay: 0.6, ease: 'power2.out' }
        );
      }
    }, heroRef);
    return () => ctx.revert();
  }, []);

  return (
    <motion.section
      ref={heroRef}
      style={{
        minHeight: '100vh',
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        justifyContent: 'center',
        position: 'relative',
        y,
        opacity,
        scale,
        padding: '20px',
      }}
    >
      {/* Top Navigation Bar */}
      <motion.div
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.8, duration: 0.5 }}
        style={{
          position: 'absolute',
          top: 0,
          left: 0,
          right: 0,
          padding: '16px clamp(16px, 4vw, 40px)',
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
          zIndex: 100,
        }}
      >
        {/* Logo */}
        <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
          <div
            style={{
              width: 36,
              height: 36,
              borderRadius: 10,
              background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              boxShadow: '0 4px 20px rgba(102, 126, 234, 0.4)',
              flexShrink: 0,
            }}
          >
            <span style={{ color: '#fff', fontSize: 16, fontWeight: 800 }}>S</span>
          </div>
          <span style={{ color: '#fff', fontSize: 'clamp(16px, 3vw, 20px)', fontWeight: 700, letterSpacing: 2 }}>
            SIONYX
          </span>
        </div>

        {/* Admin Button */}
        <AnimatedButton
          variant='ghost'
          size='small'
          icon={<CrownOutlined />}
          onClick={onAdminLogin}
          style={{
            background: 'rgba(255,255,255,0.1)',
            backdropFilter: 'blur(10px)',
            border: '1px solid rgba(255,255,255,0.2)',
            color: '#fff',
            fontSize: 'clamp(12px, 2.5vw, 14px)',
            padding: '6px 12px',
          }}
        >
          כניסת מנהל
        </AnimatedButton>
      </motion.div>

      {/* Main Title */}
      <div style={{ textAlign: 'center', marginBottom: 20 }}>
        <h1
          style={{
            fontSize: 'clamp(2.5rem, 10vw, 8rem)',
            fontWeight: 900,
            color: 'white',
            margin: 0,
            letterSpacing: '0.12em',
            fontFamily: "'Inter', 'Segoe UI', sans-serif",
            direction: 'ltr',
            display: 'flex',
            justifyContent: 'center',
            lineHeight: 1,
          }}
        >
          {'SIONYX'.split('').map((letter, i) => (
            <motion.span
              key={i}
              initial={{ opacity: 0, y: 40, scale: 0.8 }}
              animate={{ opacity: 1, y: 0, scale: 1 }}
              transition={{
                duration: 0.5,
                delay: 0.1 + i * 0.04,
                ease: [0.25, 0.46, 0.45, 0.94],
              }}
              style={{
                display: 'inline-block',
                textShadow: '0 0 80px rgba(102, 126, 234, 0.6)',
              }}
              whileHover={{
                scale: 1.1,
                color: colors.primary,
                transition: { duration: 0.2 },
              }}
            >
              {letter}
            </motion.span>
          ))}
        </h1>
      </div>

      {/* Tagline */}
      <motion.div
        ref={subtitleRef}
        style={{
          textAlign: 'center',
          marginBottom: 16,
        }}
      >
        <h2
          style={{
            fontSize: 'clamp(1.5rem, 4vw, 2.2rem)',
            fontWeight: 600,
            color: '#fff',
            margin: 0,
            lineHeight: 1.3,
          }}
        >
          ניהול זמן מחשבים והדפסות
        </h2>
      </motion.div>

      {/* Subtitle */}
      <motion.p
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ delay: 0.8, duration: 0.6 }}
        style={{
          fontSize: 'clamp(1rem, 2.5vw, 1.25rem)',
          color: 'rgba(255, 255, 255, 0.7)',
          maxWidth: 550,
          textAlign: 'center',
          lineHeight: 1.7,
          fontWeight: 400,
          marginBottom: 40,
          padding: '0 20px',
        }}
      >
        פתרון מקצועי לניהול זמני שימוש במחשבים, אישורי הדפסה ובקרת גישה למוסדות וארגונים
      </motion.p>

      {/* Trust Badges */}
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ delay: 1.4, duration: 0.5 }}
        style={{
          marginTop: 50,
          display: 'flex',
          gap: 32,
          flexWrap: 'wrap',
          justifyContent: 'center',
          alignItems: 'center',
        }}
      >
        {[
          { icon: <CheckCircleOutlined />, text: 'התקנה קלה' },
          { icon: <SafetyCertificateOutlined />, text: 'אבטחה מלאה' },
          { icon: <ThunderboltOutlined />, text: 'ביצועים מהירים' },
        ].map((badge, i) => (
          <motion.div
            key={i}
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 1.5 + i * 0.1 }}
            style={{
              display: 'flex',
              alignItems: 'center',
              gap: 8,
              color: 'rgba(255,255,255,0.6)',
              fontSize: 14,
            }}
          >
            <span style={{ color: colors.success }}>{badge.icon}</span>
            {badge.text}
          </motion.div>
        ))}
      </motion.div>

      {/* Scroll Indicator */}
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ delay: 2 }}
        style={{
          position: 'absolute',
          bottom: 30,
          display: 'flex',
          flexDirection: 'column',
          alignItems: 'center',
          gap: 8,
        }}
      >
        <Text style={{ color: 'rgba(255,255,255,0.4)', fontSize: 13 }}>גלול למטה</Text>
        <motion.div
          animate={{ y: [0, 8, 0] }}
          transition={{ duration: 1.5, repeat: Infinity, ease: 'easeInOut' }}
          style={{
            width: 28,
            height: 44,
            border: '2px solid rgba(255,255,255,0.2)',
            borderRadius: 14,
            display: 'flex',
            justifyContent: 'center',
            paddingTop: 8,
          }}
        >
          <motion.div
            animate={{ y: [0, 12, 0], opacity: [1, 0.2, 1] }}
            transition={{ duration: 1.5, repeat: Infinity, ease: 'easeInOut' }}
            style={{
              width: 4,
              height: 8,
              background: 'rgba(255,255,255,0.5)',
              borderRadius: 2,
            }}
          />
        </motion.div>
      </motion.div>
    </motion.section>
  );
});

HeroSection.displayName = 'HeroSection';

// ============================================
// Premium Feature Card Component
// ============================================
const FeatureCard = memo(({ icon, title, description, color, delay = 0 }) => {
  return (
    <motion.div
      initial={{ opacity: 0, y: 30 }}
      whileInView={{ opacity: 1, y: 0 }}
      viewport={{ once: true, margin: '-50px' }}
      transition={{ duration: 0.6, delay, ease: [0.25, 0.46, 0.45, 0.94] }}
      whileHover={{ y: -8, transition: { type: 'spring', stiffness: 300, damping: 20 } }}
      style={{ height: '100%' }}
    >
      <div
        style={{
          height: '100%',
          padding: '32px 28px',
          background: 'rgba(255,255,255,0.03)',
          backdropFilter: 'blur(20px)',
          borderRadius: 20,
          border: '1px solid rgba(255,255,255,0.08)',
          display: 'flex',
          flexDirection: 'column',
          transition: 'background 0.4s ease, border-color 0.4s ease, box-shadow 0.4s ease',
          cursor: 'default',
        }}
        onMouseEnter={e => {
          e.currentTarget.style.background = 'rgba(255,255,255,0.06)';
          e.currentTarget.style.borderColor = `${color}40`;
          e.currentTarget.style.boxShadow = `0 20px 40px rgba(0,0,0,0.2), 0 0 60px ${color}15`;
        }}
        onMouseLeave={e => {
          e.currentTarget.style.background = 'rgba(255,255,255,0.03)';
          e.currentTarget.style.borderColor = 'rgba(255,255,255,0.08)';
          e.currentTarget.style.boxShadow = 'none';
        }}
      >
        {/* Icon Container */}
        <div
          style={{
            width: 64,
            height: 64,
            borderRadius: 16,
            background: `linear-gradient(135deg, ${color}20 0%, ${color}10 100%)`,
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            marginBottom: 24,
            border: `1px solid ${color}30`,
          }}
        >
          <span style={{ fontSize: 28, color }}>{icon}</span>
        </div>

        {/* Title */}
        <h3
          style={{
            color: '#fff',
            fontSize: 20,
            fontWeight: 600,
            margin: '0 0 12px 0',
            lineHeight: 1.3,
          }}
        >
          {title}
        </h3>

        {/* Description */}
        <p
          style={{
            color: 'rgba(255,255,255,0.6)',
            fontSize: 15,
            lineHeight: 1.7,
            margin: 0,
            flex: 1,
          }}
        >
          {description}
        </p>
      </div>
    </motion.div>
  );
});

FeatureCard.displayName = 'FeatureCard';

// ============================================
// Features Section Component - Premium v2.0
// ============================================
const FeaturesSection = memo(() => {
  const features = [
    {
      icon: <ClockCircleOutlined />,
      title: 'ניהול זמן חכם',
      description:
        'שליטה מלאה בזמני השימוש במחשבים עם ממשק אינטואיטיבי. הגדר מגבלות יומיות, שבועיות או חודשיות.',
      color: colors.primary,
    },
    {
      icon: <PrinterOutlined />,
      title: 'בקרת הדפסות',
      description: 'ניהול אישורי הדפסה לכל משתמש. עקוב אחר כמויות הדפסה והגדר מכסות חכמות.',
      color: colors.orange,
    },
    {
      icon: <DashboardOutlined />,
      title: 'דשבורד מתקדם',
      description: 'סטטיסטיקות מפורטות ונתונים בזמן אמת על פעילות המשתמשים והמחשבים.',
      color: colors.cyan,
    },
    {
      icon: <TeamOutlined />,
      title: 'ניהול משתמשים',
      description: 'הוספה, עריכה וניהול משתמשים בקלות. הגדר הרשאות והקצאות לכל משתמש.',
      color: colors.success,
    },
    {
      icon: <SafetyCertificateOutlined />,
      title: 'אבטחה מתקדמת',
      description: 'הגנה על הארגון עם מערכת הרשאות חכמה, בקרות גישה והצפנת נתונים.',
      color: colors.secondary,
    },
    {
      icon: <CloudOutlined />,
      title: 'גיבוי ענן',
      description: 'כל הנתונים מגובים בענן באופן אוטומטי. גישה מכל מקום בכל זמן.',
      color: colors.info,
    },
  ];

  return (
    <section style={{ padding: '100px 20px', position: 'relative', zIndex: 1 }}>
      {/* Section Header */}
      <motion.div
        initial={{ opacity: 0, y: 30 }}
        whileInView={{ opacity: 1, y: 0 }}
        viewport={{ once: true }}
        transition={{ duration: 0.6 }}
        style={{ textAlign: 'center', marginBottom: 70, maxWidth: 700, margin: '0 auto 70px' }}
      >
        <motion.div
          initial={{ opacity: 0, scale: 0.9 }}
          whileInView={{ opacity: 1, scale: 1 }}
          viewport={{ once: true }}
          transition={{ duration: 0.5 }}
        >
          <Tag
            style={{
              background: 'rgba(102, 126, 234, 0.15)',
              border: '1px solid rgba(102, 126, 234, 0.3)',
              borderRadius: 20,
              padding: '5px 14px',
              color: colors.primaryLight,
              fontSize: 13,
              fontWeight: 500,
              marginBottom: 20,
            }}
          >
            יתרונות המערכת
          </Tag>
        </motion.div>

        <Title
          level={2}
          style={{
            color: 'white',
            fontSize: 'clamp(1.8rem, 4vw, 2.5rem)',
            fontWeight: 700,
            marginBottom: 16,
            lineHeight: 1.3,
          }}
        >
          כל מה שצריך לניהול יעיל
        </Title>

        <Paragraph
          style={{
            color: 'rgba(255,255,255,0.6)',
            fontSize: 'clamp(1rem, 2vw, 1.1rem)',
            margin: 0,
            lineHeight: 1.7,
          }}
        >
          מערכת SIONYX מספקת את כל הכלים הנדרשים לניהול זמני מחשב והדפסות בארגון שלך
        </Paragraph>
      </motion.div>

      {/* Features Grid */}
      <Row gutter={[24, 24]} justify='center' style={{ maxWidth: 1200, margin: '0 auto' }}>
        {features.map((feature, index) => (
          <Col xs={24} sm={12} lg={8} key={index}>
            <FeatureCard
              icon={feature.icon}
              title={feature.title}
              description={feature.description}
              color={feature.color}
              delay={index * 0.08}
            />
          </Col>
        ))}
      </Row>
    </section>
  );
});

FeaturesSection.displayName = 'FeaturesSection';

// ============================================
// Stats Section Component - Social Proof
// ============================================
const StatsSection = memo(() => {
  const stats = [
    { value: '50+', label: 'ארגונים פעילים', color: colors.primary },
    { value: '1,000+', label: 'משתמשים רשומים', color: colors.success },
    { value: '99.9%', label: 'זמינות שרת', color: colors.cyan },
    { value: '24/6', label: 'תמיכה טכנית', color: colors.warning },
  ];

  return (
    <section style={{ padding: '60px 20px', position: 'relative', zIndex: 1 }}>
      <div
        style={{
          maxWidth: 1000,
          margin: '0 auto',
          background: 'rgba(255,255,255,0.03)',
          backdropFilter: 'blur(20px)',
          borderRadius: 24,
          border: '1px solid rgba(255,255,255,0.08)',
          padding: '40px 20px',
        }}
      >
        <Row gutter={[20, 30]} justify='center' align='middle'>
          {stats.map((stat, index) => (
            <Col xs={12} sm={6} key={index}>
              <motion.div
                initial={{ opacity: 0, y: 20 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true, margin: '-50px' }}
                transition={{ delay: index * 0.12, duration: 0.6, ease: [0.25, 0.46, 0.45, 0.94] }}
                style={{ textAlign: 'center' }}
              >
                <div
                  style={{
                    fontSize: 'clamp(2rem, 5vw, 2.8rem)',
                    fontWeight: 800,
                    color: stat.color,
                    lineHeight: 1.2,
                    marginBottom: 8,
                  }}
                >
                  {stat.value}
                </div>
                <div
                  style={{
                    fontSize: 'clamp(0.8rem, 2vw, 0.95rem)',
                    color: 'rgba(255,255,255,0.6)',
                    fontWeight: 500,
                  }}
                >
                  {stat.label}
                </div>
              </motion.div>
            </Col>
          ))}
        </Row>
      </div>
    </section>
  );
});

StatsSection.displayName = 'StatsSection';

// ============================================
// Action Cards Section Component - Premium v3.0
// ============================================
const ActionCardsSection = memo(
  ({ onAdminLogin }) => {
    return (
      <section
        style={{
          padding: '80px 20px 100px',
          position: 'relative',
          zIndex: 1,
          display: 'flex',
          flexDirection: 'column',
          alignItems: 'center',
        }}
      >
        {/* Section Header */}
        <motion.div
          initial={{ opacity: 0, y: 30 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true, margin: '-80px' }}
          transition={{ duration: 0.7, ease: [0.25, 0.46, 0.45, 0.94] }}
          style={{ textAlign: 'center', marginBottom: 50, width: '100%' }}
        >
          <Title
            level={2}
            style={{
              color: 'white',
              fontSize: 'clamp(1.8rem, 4vw, 2.5rem)',
              fontWeight: 700,
              marginBottom: 16,
              textAlign: 'center',
            }}
          >
            מוכן להתחיל?
          </Title>
          <Paragraph
            style={{
              color: 'rgba(255,255,255,0.6)',
              fontSize: 'clamp(1rem, 2vw, 1.1rem)',
              margin: '0 auto',
              textAlign: 'center',
            }}
          >
            בחר את הפעולה המתאימה לך
          </Paragraph>
        </motion.div>

        <Row gutter={[24, 24]} justify='center' style={{ maxWidth: 1100, margin: '0 auto' }}>
          {/* Already Registered Card */}
          <Col xs={24} md={12}>
            <motion.div
              initial={{ opacity: 0, y: 30 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true, margin: '-60px' }}
              transition={{ delay: 0.25, duration: 0.6, ease: [0.25, 0.46, 0.45, 0.94] }}
              whileHover={{ y: -6, transition: { type: 'spring', stiffness: 300, damping: 20 } }}
              style={{ height: '100%' }}
            >
              <div
                style={{
                  height: '100%',
                  padding: '36px 32px',
                  textAlign: 'center',
                  background: 'rgba(255,255,255,0.03)',
                  backdropFilter: 'blur(20px)',
                  borderRadius: 20,
                  border: '1px solid rgba(255,255,255,0.08)',
                  display: 'flex',
                  flexDirection: 'column',
                }}
              >
                <div
                  style={{
                    width: 64,
                    height: 64,
                    borderRadius: 16,
                    background: `linear-gradient(135deg, ${colors.warning}20 0%, ${colors.warning}10 100%)`,
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    margin: '0 auto 20px',
                    border: `1px solid ${colors.warning}30`,
                  }}
                >
                  <CrownOutlined style={{ fontSize: 28, color: colors.warning }} />
                </div>

                <h3 style={{ color: 'white', margin: '0 0 8px', fontSize: 22, fontWeight: 600 }}>
                  כבר רשום?
                </h3>

                <p
                  style={{
                    color: 'rgba(255,255,255,0.6)',
                    marginBottom: 24,
                    flex: 1,
                    fontSize: 15,
                  }}
                >
                  היכנס לפאנל הניהול לצפייה בנתונים וניהול המשתמשים
                </p>

                <AnimatedButton
                  variant='warning'
                  size='large'
                  icon={<CrownOutlined />}
                  onClick={onAdminLogin}
                  fullWidth
                  style={{
                    background: colors.warning,
                    borderColor: colors.warning,
                  }}
                >
                  כניסה לפאנל ניהול
                </AnimatedButton>
              </div>
            </motion.div>
          </Col>
        </Row>
      </section>
    );
  }
);

ActionCardsSection.displayName = 'ActionCardsSection';

// ============================================
// Main Landing Page Component
// ============================================
const LandingPage = memo(() => {
  const navigate = useNavigate();

  const handleAdminLogin = useCallback(() => {
    navigate('/login');
  }, [navigate]);

  return (
    <div
      style={{
        minHeight: '100vh',
        direction: 'rtl',
        position: 'relative',
        overflow: 'hidden',
      }}
    >
      {/* Animated Background */}
      <AnimatedBackground />

      {/* Content */}
      <div style={{ position: 'relative', zIndex: 1 }}>
        {/* Hero Section */}
        <HeroSection
          onAdminLogin={handleAdminLogin}
        />

        {/* Features Section */}
        <FeaturesSection />

        {/* Stats Section - Social Proof */}
        <StatsSection />

        {/* Action Cards Section */}
        <ActionCardsSection
          onAdminLogin={handleAdminLogin}
        />

        {/* Premium Footer */}
        <motion.footer
          initial={{ opacity: 0 }}
          whileInView={{ opacity: 1 }}
          viewport={{ once: true }}
          style={{
            padding: '60px 20px 40px',
            borderTop: '1px solid rgba(255,255,255,0.05)',
          }}
        >
          <div style={{ maxWidth: 1100, margin: '0 auto' }}>
            {/* Footer Top */}
            <Row gutter={[40, 40]} justify='space-between' align='top'>
              {/* Brand */}
              <Col xs={24} md={8}>
                <div style={{ display: 'flex', alignItems: 'center', gap: 12, marginBottom: 16 }}>
                  <div
                    style={{
                      width: 44,
                      height: 44,
                      borderRadius: 12,
                      background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'center',
                    }}
                  >
                    <span style={{ color: '#fff', fontSize: 20, fontWeight: 800 }}>S</span>
                  </div>
                  <span style={{ color: '#fff', fontSize: 22, fontWeight: 700, letterSpacing: 2 }}>
                    SIONYX
                  </span>
                </div>
                <p
                  style={{
                    color: 'rgba(255,255,255,0.5)',
                    fontSize: 14,
                    lineHeight: 1.7,
                    margin: 0,
                  }}
                >
                  פתרון מתקדם לניהול זמן מחשבים ואישורי הדפסה למוסדות וארגונים.
                </p>
              </Col>

              {/* Quick Links */}
              <Col xs={12} md={4}>
                <h4 style={{ color: '#fff', fontSize: 15, fontWeight: 600, marginBottom: 16 }}>
                  קישורים מהירים
                </h4>
                <div style={{ display: 'flex', flexDirection: 'column', gap: 10 }}>
                  {[
                    {
                      label: 'דף הבית',
                      action: () => window.scrollTo({ top: 0, behavior: 'smooth' }),
                    },
                    { label: 'כניסת מנהל', action: handleAdminLogin },
                  ].map((link, i) => (
                    <a
                      key={i}
                      onClick={link.action}
                      style={{
                        color: 'rgba(255,255,255,0.5)',
                        fontSize: 14,
                        cursor: 'pointer',
                        transition: 'color 0.2s',
                      }}
                      onMouseEnter={e => (e.currentTarget.style.color = colors.primaryLight)}
                      onMouseLeave={e => (e.currentTarget.style.color = 'rgba(255,255,255,0.5)')}
                    >
                      {link.label}
                    </a>
                  ))}
                </div>
              </Col>

              {/* Contact */}
              <Col xs={12} md={4}>
                <h4 style={{ color: '#fff', fontSize: 15, fontWeight: 600, marginBottom: 16 }}>
                  יצירת קשר
                </h4>
                <div style={{ display: 'flex', flexDirection: 'column', gap: 10 }}>
                  <span style={{ color: 'rgba(255,255,255,0.5)', fontSize: 14 }}>
                    <MailOutlined style={{ marginLeft: 8 }} />
                    moshesionov340@gmail.com
                  </span>
                  <span style={{ color: 'rgba(255,255,255,0.5)', fontSize: 14 }}>
                    <PhoneOutlined style={{ marginLeft: 8 }} />
                    054-8477910
                  </span>
                </div>
              </Col>
            </Row>

            {/* Divider */}
            <div
              style={{
                height: 1,
                background: 'rgba(255,255,255,0.08)',
                margin: '40px 0 24px',
              }}
            />

            {/* Footer Bottom */}
            <div
              style={{
                display: 'flex',
                justifyContent: 'space-between',
                alignItems: 'center',
                flexWrap: 'wrap',
                gap: 16,
              }}
            >
              <Text style={{ color: 'rgba(255,255,255,0.4)', fontSize: 13 }}>
                © 2026 SIONYX. כל הזכויות שמורות.
              </Text>
              <div style={{ display: 'flex', gap: 20 }}>
                {['תנאי שימוש', 'מדיניות פרטיות'].map((item, i) => (
                  <a
                    key={i}
                    href='#'
                    style={{
                      color: 'rgba(255,255,255,0.4)',
                      fontSize: 13,
                      textDecoration: 'none',
                      transition: 'color 0.2s',
                    }}
                    onMouseEnter={e => (e.currentTarget.style.color = 'rgba(255,255,255,0.7)')}
                    onMouseLeave={e => (e.currentTarget.style.color = 'rgba(255,255,255,0.4)')}
                  >
                    {item}
                  </a>
                ))}
              </div>
            </div>
          </div>
        </motion.footer>
      </div>
    </div>
  );
});

LandingPage.displayName = 'LandingPage';

export default LandingPage;
