from app import create_app

app = create_app()

if __name__ == '__main__':
    print("\n" + "=" * 60)
    print("🚀 STUDENT PERFORMANCE MONITORING SYSTEM")
    print("=" * 60)
    print("\n✅ Server is starting...")
    print("🌐 Open your browser and go to: http://localhost:5000")
    print("\n📝 Default Login Credentials:")
    print("   👑 Admin:  admin / admin123")
    print("   👨‍🎓 Student: john_doe / password123")
    print("\n⚠️  Press CTRL+C to stop the server")
    print("=" * 60 + "\n")

    app.run(debug=True, host='localhost', port=5000)