import unittest


class TestDom(unittest.TestCase):
    # NOTE unfunished

    async def test_human_like_mouse_move(
        self, 
        start_x:int, 
        start_y:int, 
        end_x:int, 
        end_y:int
    ):
        """Moves the mouse cursor in a sin-wave pattern to appear more humanlike.

        *This function is for testing purposes! There is JS here to track the cursor
        movements and print them to the terminal.
        """
        await self.page.evaluate('''() => {
            window.mousePositions = [];
            document.addEventListener('mousemove', event => {
                window.mousePositions.push({x: event.clientX, y: event.clientY});
            });
        }''')

        path = self._generate_curved_path(start_x, start_y, end_x, end_y)
        for x, y in path:
            await self.page.mouse.move(x, y)
            await async_sleep(random.uniform(0.05, 0.15))
            position = await self.page.evaluate('window.mousePositions[window.mousePositions.length - 1]')
            print(f"Mouse moved to: {position}")
