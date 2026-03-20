from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel, Field
from typing import Optional

app = FastAPI()

# Fake Database

courses = [
    {"id": 1, "title": "React for Beginners", "instructor": "John", "category": "Web Dev", "level": "Beginner", "price": 0, "seats_left": 10, "popularity": 5},
    {"id": 2, "title": "Advanced Python", "instructor": "Alice", "category": "Data Science", "level": "Advanced", "price": 5000, "seats_left": 5, "popularity": 8},
    {"id": 3, "title": "UI/UX Design", "instructor": "David", "category": "Design", "level": "Intermediate", "price": 3000, "seats_left": 8, "popularity": 6},
    {"id": 4, "title": "Docker & DevOps", "instructor": "Chris", "category": "DevOps", "level": "Intermediate", "price": 4000, "seats_left": 6, "popularity": 7},
    {"id": 5, "title": "Machine Learning Basics", "instructor": "Emma", "category": "Data Science", "level": "Beginner", "price": 2000, "seats_left": 12, "popularity": 9},
    {"id": 6, "title": "Next.js Mastery", "instructor": "Mark", "category": "Web Dev", "level": "Advanced", "price": 4500, "seats_left": 4, "popularity": 10},
]

enrollments = []
wishlist = []
enrollment_counter = 1

# Models

# Q6 -  Validates student enrollment data (name, course_id, email, payment, coupon, gift

class EnrollRequest(BaseModel):
    student_name: str = Field(..., min_length=2)
    course_id: int = Field(..., gt=0)
    email: str = Field(..., min_length=5)
    payment_method: str = "card"
    coupon_code: str = ""
    gift_enrollment: bool = False
    recipient_name: str = ""

class NewCourse(BaseModel):
    title: str = Field(..., min_length=2)
    instructor: str = Field(..., min_length=2)
    category: str = Field(..., min_length=2)
    level: str = Field(..., min_length=2)
    price: int = Field(..., ge=0)
    seats_left: int = Field(..., gt=0)

# Q7 - Helper Functions

def find_course(course_id):
    for c in courses:
        if c["id"] == course_id:
            return c
    return None

def calculate_enrollment_fee(price, seats_left, coupon_code):
    discount = 0

    # Early bird
    if seats_left > 5:
        discount += 0.1 * price

    # Dynamic pricing (NEW)
    if seats_left < 3:
        price += 500

    # Coupons
    if coupon_code == "STUDENT20":
        discount += 0.2 * price
    elif coupon_code == "FLAT500":
        discount += 500

    final = max(price - discount, 0)

    return round(final, 2), discount

def filter_courses_logic(category, level, max_price, has_seats):
    result = courses
    if category is not None:
        result = [c for c in result if c["category"] == category]
    if level is not None:
        result = [c for c in result if c["level"] == level]
    if max_price is not None:
        result = [c for c in result if c["price"] <= max_price]
    if has_seats is not None:
        result = [c for c in result if (c["seats_left"] > 0) == has_seats]
    return result

# Q1 - Returns a welcome message

@app.get("/")
def home():
    return {"message": "Welcome to LearnHub Online Courses"}

# Q2 -  Lists all courses, total count, and total seats available.

@app.get("/courses")
def get_courses():
    total_seats = sum(c["seats_left"] for c in courses)
    return {"courses": courses, "total": len(courses), "total_seats": total_seats}

# Q5 - Returns stats: total courses, free courses, most expensive, total seats, category count

@app.get("/courses/summary")
def summary():
    return {
        "total": len(courses),
        "free": len([c for c in courses if c["price"] == 0]),
        "most_expensive": max(courses, key=lambda x: x["price"]),
        "total_seats": sum(c["seats_left"] for c in courses)
    }

# Q3 - Returns details for a specific course or 404 if not found.

@app.get("/courses/{course_id}")
def get_course(course_id: int):
    c = find_course(course_id)
    if not c:
        raise HTTPException(404, "Course not found")
    return c

# Q4 - Lists all enrollments and total count

@app.get("/enrollments")
def get_enrollments():
    return {"data": enrollments, "total": len(enrollments)}

# Q8 + Q9 -Enrolls a student, checks seats, applies discounts, returns enrollment details &  Validates recipient for gift enrollments, records recipient in enrollment

@app.post("/enrollments")
def enroll(data: EnrollRequest):
    global enrollment_counter

    course = find_course(data.course_id)
    if not course:
        raise HTTPException(404, "Course not found")

    if course["seats_left"] <= 0:
        raise HTTPException(400, "No seats available")

    if data.gift_enrollment and data.recipient_name == "":
        raise HTTPException(400, "Recipient required")

    final_fee, discount = calculate_enrollment_fee(course["price"], course["seats_left"], data.coupon_code)

    course["seats_left"] -= 1
    course["popularity"] += 1

    record = {
        "id": enrollment_counter,
        "student": data.student_name,
        "course": course["title"],
        "final_fee": final_fee,
        "discount": discount
    }

    enrollment_counter += 1
    enrollments.append(record)

    return record


# Q10 - Filters courses by category, level, price, and seat availability

@app.get("/courses/filter")
def filter_courses(category: Optional[str] = None,
                   level: Optional[str] = None,
                   max_price: Optional[int] = None,
                   has_seats: Optional[bool] = None):
    return filter_courses_logic(category, level, max_price, has_seats)

# Q11 -Adds new course, validates fields, rejects duplicate titles

@app.post("/courses", status_code=201)
def create_course(data: NewCourse):
    if any(c["title"] == data.title for c in courses):
        raise HTTPException(400, "Duplicate title")

    new = data.dict()
    new["id"] = len(courses) + 1
    new["popularity"] = 0
    courses.append(new)
    return new

# Q12 - Updates course price/seats, only if provided, returns 404 if not found

@app.put("/courses/{course_id}")
def update_course(course_id: int, price: Optional[int] = None, seats_left: Optional[int] = None):
    c = find_course(course_id)
    if not c:
        raise HTTPException(404, "Not found")

    if price is not None:
        c["price"] = price
    if seats_left is not None:
        c["seats_left"] = seats_left

    return c

# Q13 - Deletes course if no enrollments reference it, else returns error

@app.delete("/courses/{course_id}")
def delete_course(course_id: int):
    c = find_course(course_id)
    if not c:
        raise HTTPException(404, "Not found")

    for e in enrollments:
        if e["course"] == c["title"]:
            raise HTTPException(400, "Course has enrollments")

    courses.remove(c)
    return {"message": "Deleted"}

# Q14 -POST /wishlist/add adds course to wishlist, GET /wishlist returns wishlist and total value

@app.post("/wishlist/add")
def add_wishlist(student_name: str, course_id: int):
    if any(w["student"] == student_name and w["course_id"] == course_id for w in wishlist):
        raise HTTPException(400, "Duplicate")

    wishlist.append({"student": student_name, "course_id": course_id})
    return {"message": "Added"}

@app.get("/wishlist")
def get_wishlist():
    total_value = 0
    for w in wishlist:
        c = find_course(w["course_id"])
        if c:
            total_value += c["price"]
    return {"wishlist": wishlist, "total_value": total_value}

# Q15 -DELETE /wishlist/remove/{course_id} removes item, POST /wishlist/enroll-all enrolls all wishlist courses for a student.

@app.delete("/wishlist/remove/{course_id}")
def remove_wishlist(course_id: int, student_name: str):
    for w in wishlist:
        if w["course_id"] == course_id and w["student"] == student_name:
            wishlist.remove(w)
            return {"message": "Removed"}
    raise HTTPException(404, "Not found")

@app.post("/wishlist/enroll-all")
def enroll_all(student_name: str, payment_method: str):
    total = 0
    enrolled = []

    for w in wishlist[:]:
        if w["student"] == student_name:
            course = find_course(w["course_id"])
            if course and course["seats_left"] > 0:
                fee, _ = calculate_enrollment_fee(course["price"], course["seats_left"], "")
                total += fee
                enrolled.append(course["title"])
                course["seats_left"] -= 1
                wishlist.remove(w)

    return {"enrolled": enrolled, "total_fee": total}

# Q16 -Searches courses by keyword across title, instructor, and category (case-insensitive)

@app.get("/courses/search")
def search(keyword: str):
    result = [c for c in courses if keyword.lower() in c["title"].lower()
              or keyword.lower() in c["instructor"].lower()
              or keyword.lower() in c["category"].lower()]
    return {"results": result, "total": len(result)}

# Q17 -Sorts courses by price, title, or seats_left.

@app.get("/courses/sort")
def sort(sort_by: str = "price"):
    return sorted(courses, key=lambda x: x.get(sort_by, 0))

# Q18 - Paginates courses with page and limit, returns correct slice

@app.get("/courses/page")
def paginate(page: int = 1, limit: int = 3):
    start = (page - 1) * limit
    end = start + limit
    return {"data": courses[start:end]}

# Q19 -  GET /enrollments/search, /sort, /page for searching, sorting, and paginating enrollments.

@app.get("/enrollments/search")
def search_enroll(student_name: str):
    return [e for e in enrollments if student_name.lower() in e["student"].lower()]

@app.get("/enrollments/sort")
def sort_enroll():
    return sorted(enrollments, key=lambda x: x["final_fee"])

@app.get("/enrollments/page")
def page_enroll(page: int = 1, limit: int = 2):
    start = (page - 1) * limit
    return enrollments[start:start+limit]

# Q20 - Combines keyword search, filters, sorting, and pagination for advanced browsing.

@app.get("/courses/browse")
def browse(keyword: Optional[str] = None,
           category: Optional[str] = None,
           level: Optional[str] = None,
           max_price: Optional[int] = None,
           page: int = 1,
           limit: int = 3):

    result = courses

    if keyword:
        result = [c for c in result if keyword.lower() in c["title"].lower()]

    if category:
        result = [c for c in result if c["category"] == category]

    if level:
        result = [c for c in result if c["level"] == level]

    if max_price:
        result = [c for c in result if c["price"] <= max_price]

    start = (page - 1) * limit
    return {
        "results": result[start:start+limit],
        "total": len(result)
    }