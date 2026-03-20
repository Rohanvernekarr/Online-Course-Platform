# LearnHub Online Course Platform

This project is a FastAPI-based REST API for managing an online course platform. Below is a summary of the 20 implemented endpoints:

## Day 1 
1. **GET /** - Returns a welcome message.
2. **GET /courses** - Lists all courses, total count, and total seats available.
3. **GET /courses/{course_id}** - Returns details for a specific course or 404 if not found.
4. **GET /enrollments** - Lists all enrollments and total count.
5. **GET /courses/summary** - Returns stats: total courses, free courses, most expensive, total seats, category count.

## Day 2–3 
6. **EnrollRequest model** - Validates student enrollment data (name, course_id, email, payment, coupon, gift).
7. **find_course & calculate_enrollment_fee** - Helper functions for course lookup and fee calculation (discounts, coupons).
8. **POST /enrollments** - Enrolls a student, checks seats, applies discounts, returns enrollment details.
9. **Gift enrollment logic** - Validates recipient for gift enrollments, records recipient in enrollment.
10. **GET /courses/filter** - Filters courses by category, level, price, and seat availability.

## Day 4–5
11. **NewCourse model & POST /courses** - Adds new course, validates fields, rejects duplicate titles.
12. **PUT /courses/{course_id}** - Updates course price/seats, only if provided, returns 404 if not found.
13. **DELETE /courses/{course_id}** - Deletes course if no enrollments reference it, else returns error.
14. **Wishlist logic** - POST /wishlist/add adds course to wishlist, GET /wishlist returns wishlist and total value.
15. **Wishlist bulk enroll** - DELETE /wishlist/remove/{course_id} removes item, POST /wishlist/enroll-all enrolls all wishlist courses for a student.

## Day 6 
16. **GET /courses/search** - Searches courses by keyword across title, instructor, and category (case-insensitive).
17. **GET /courses/sort** - Sorts courses by price, title, or seats_left.
18. **GET /courses/page** - Paginates courses with page and limit, returns correct slice.
19. **Enrollments search/sort/page** - GET /enrollments/search, /sort, /page for searching, sorting, and paginating enrollments.
20. **GET /courses/browse** - Combines keyword search, filters, sorting, and pagination for advanced browsing.

---

Each endpoint is implemented in main.py. See the file for full code and logic. Run the FastAPI app and use tools like Swagger UI or Postman to test all endpoints.
